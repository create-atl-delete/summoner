import logging
import re
import sys
from configparser import ConfigParser, NoOptionError, NoSectionError
from pathlib import Path
from typing import Literal

from pick import pick

from summoner.conf.connection_funcs import CONNECTION_FUNCS
from summoner.evocation import Action, Evocation
from summoner.lib.boto import BotoEnhanced, get_instance_status
from summoner.lib.const import DEFAULT_INSTANCE, SUMMONER_FOLDER
from summoner.lib.instance import Instance
from summoner.util import get_instance, status_manager

LOGGER = logging.getLogger()


class Summoner:
    def __init__(
        self,
        mode: Literal["instance", "config", "select"],
        config_file: Path | None = None,
        aws_profile: str | None = None,
        sts_arn: str | None = None,
        region: str | None = None,
        instance_id: str | None = None,
        connection_type: str | None = None,
        domain: str | None = None,
        username: str | None = None,
        local_port: str | None = None,
    ):
        self.mode = mode
        if config_file:
            self.config_file = Path(SUMMONER_FOLDER, config_file)  # type: ignore

        self.base_instance = Instance
        self.boto_session = None
        self.connect_funcs = CONNECTION_FUNCS
        self.instances = []

        if self.mode == "instance":
            self._load_instance(
                aws_profile, sts_arn, region, instance_id, connection_type, domain, username, local_port
            )
        elif self.mode == "select":
            self._load_selection(aws_profile, sts_arn, region)
        elif self.mode == "config":
            if self.config_file.exists():
                self._load_config()
            else:
                self.config_menu()

        self.main_menu()

    def add_connection_type(self, name, func, port):
        self.base_instance.add_connection_type(name, port)
        self.connect_funcs.update({name, func})

    def main_menu(self):
        opt = ["Connect", "Manage", "Config", "Quit"]
        while True:
            cat, _ = pick(opt, "What would you like to do?")
            if cat == "Connect":
                self.connect_menu()
            elif cat == "Manage":
                self.manage_menu()
            elif cat == "Config":
                self.config_menu()
            elif cat == "Quit":
                break

    def _load_selection(self, aws_profile, sts_arn, region):
        self.boto_session = BotoEnhanced(region, aws_profile, sts_arn)

        ec2_client = self.boto_session.resource("ec2")
        instance_ids = [instance.id for instance in ec2_client.instances.all()]  # type: ignore
        instance_id, _ = pick(instance_ids + ["Quit"])
        if instance_id == "Quit":
            return

        connection_type, _ = pick(["rdp", "ssh", "vnc"])
        username = input("Enter username: ")
        domain = input("Enter domain: ")
        if local_port := input("Local port: "):
            local_port = int(local_port)

        try:
            self.instances.append(self.base_instance("selected", region, instance_id, connection_type, domain, username, local_port))  # type: ignore
        except AttributeError as ex:
            raise Exception(f"Could not parameterize Instance using provided args. Error {ex}")

    def _load_instance(self, aws_profile, sts_arn, region, instance_id, connection_type, domain, username, local_port):
        self.boto_session = BotoEnhanced(region, aws_profile, sts_arn)

        try:
            self.instances.append(
                self.base_instance("given", region, instance_id, connection_type, domain, username, local_port)
            )
        except AttributeError as ex:
            raise Exception(f"Could not parameterize Instance using provided args. Error {ex}")

    def _load_config(self):


        config = ConfigParser()
        config.read(self.config_file)

        try:
            aws_profile = config.get("config-settings", "aws_profile")
            sts_arn = config.get("config-settings", "sts_arn")
            region = config.get(config.sections()[-1], "region")
        except (NoSectionError, NoOptionError):
            self.config_menu()
            return

        try:
            self.boto_session = BotoEnhanced(region, aws_profile, sts_arn)
        except KeyError as ex:
            raise Exception(f"No aws_profile setting in config! {ex}")

        instances = []
        for i in [i for i in config.sections() if i != "config-settings"]:
            try:
                instances[i] = self.base_instance(**dict(config[i].items()))  # type: ignore
            except AttributeError as ex:
                LOGGER.exception(f"Invalid Instance, {i}. Error: {ex}")

    def config_menu(self):

        def delete_instance(instance):
            config.remove_section(instance)

        def update_instance(instance):
            if instance["name"] not in config.sections():
                config.read_dict({instance["name"]: instance})

            update = input(f" - Name [{instance["name"]}]: ")
            if update:
                config.read_dict({update: instance})
                config.set(update, "name", update)
                config.remove_section(instance["name"])
                instance["name"] = update

            update = input(f" - Domain (enter 'None' to unset) [{instance.get('domain')}]: ")
            if update and update != "None":
                config.set(instance["name"], "domain", update)
            elif update == "None":
                config.remove_option(instance["name"], "domain")

            update = input(f" - Username (enter 'None' to unset) [{instance.get('username')}]: ")
            if update and update != "None":
                config.set(instance["name"], "username", update)
            elif update == "None":
                config.remove_option(instance["name"], "username")

            while True:
                update = input(f" - Local Port (enter 'None' to unset) [{instance.get('local_port')}]: ")
                if update and update != "None":
                    if int(update) in range(50000, 60000):
                        config.set(instance["name"], "local_port", update)
                        break
                    print("Invalid port. Should be None or a number between 50000 and 60000.")
                elif update == "None":
                    config.remove_option(instance["name"], "local_port")
                    break
                else:
                    break

            while True:
                update = input(f" - Connection type [{instance['connection_type']}]: ")
                if update:
                    if update.lower() in self.base_instance.connection_types:
                        config.set(instance["name"], "connection_type", update.lower())
                        break
                    print(f"Invalid Connection type. Should be one of: {self.base_instance.connection_types}")
                else:
                    break

            while True:
                update = input(f" - Region [{instance['region']}]: ")
                if update:
                    if re.match("^[a-z]{2}-(gov-)*[a-z]+-\\d$", update):
                        config.set(instance["name"], "region", update)
                        break
                    print("Invalid Region.")
                else:
                    break

            while True:
                update = input(f" - Instance ID [{instance['instance_id']}]: ")
                if update:
                    if re.match("^i-[a-f0-9]{17}$", update):
                        config.set(instance["name"], "instance_id", update)
                        break
                    print("Invalid Instance ID.")
                else:
                    break

        def update_config():
            if "config-settings" not in config.sections():
                config.add_section("config-settings")

            update = input(f" - AWS Profile [{config['config-settings'].get('aws_profile')}]: ")
            if update:
                config.set("config-settings", "aws_profile", update)

            while True:
                update = input(f" - STS ARN (enter 'None' to unset) [{config['config-settings'].get('sts_arn')}]: ")
                if update and update != "None":
                    if re.match("^arn:aws:iam::\\d{12}:role/.*$", update):
                        config.set("config-settings", "sts_arn", update)
                        break
                    print("Invalid STS ARN.")
                elif update == "None":
                    config.remove_option(instance["name"], "local_port")
                    break
                else:
                    break

        print(
            f"Creating/updating {self.config_file.name} account config."
            "Press ENTER to accept the [current value] for applicable settings."
        )

        config = ConfigParser()
        config.read(self.config_file)

        while True:
            instances = [f"Update {i}" for i in config.sections() if i != "config-settings"]
            opt, _ = pick(["Config Settings", "Add Instance"] + instances + ["<== Back", "<== Quit"], "Update what?")

            if opt == "<== Back":
                break
            elif opt == "<== Quit":
                sys.exit(0)
            elif opt == "Config Settings":
                update_config()
            elif opt == "Add Instance":
                update_instance(DEFAULT_INSTANCE)
            else:
                instance = dict(config[opt.replace("Update", "").strip()].items())  # type: ignore
                opt, _ = pick(["Update", "Delete", "<== Back"], f"What do you want to do with {instance['name']}?")
                if opt == "<== Back":
                    pass
                elif opt == "Delete":
                    delete_instance(instance)
                elif opt == "Update":
                    update_instance(instance)

        with open(self.config_file, "w") as f0:
            config.write(f0)

        self._load_config()

    def connect_menu(self):
        while True:
            if not (target := get_instance(self.instances)):
                break

            if self.mode == "instance":
                stop_on_connection_end = get_instance_status(self.boto_session, target) == "stopped"  # type: ignore
            else:
                stop_on_connection_end = False

            if not status_manager(self.boto_session, target, connecting=True):  # type: ignore
                break

            connect_func = Action(self.connect_funcs[target.connection_type])  # type: ignore
            Evocation(self.boto_session, target).connect(connect_func)  # type: ignore

            if stop_on_connection_end:
                status_manager(self.boto_session, target, stopping=True)  # type: ignore
            else:
                status_manager(self.boto_session, target)  # type: ignore

    def manage_menu(self):
        while True:
            if not (target := get_instance(self.instances)):
                break

            status_manager(self.boto_session, target)  # type: ignore
