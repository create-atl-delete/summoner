import logging
import time
from typing import List

from boto3 import Session
from pick import pick

from summoner.lib.boto import BotoEnhanced, get_instance_status, start_instance, stop_instance
from summoner.lib.instance import Instance

LOGGER = logging.getLogger()


def get_instance(instances: List[Instance]) -> Instance | None:
    """Returns a user-selected Instance from a list of Instances."""
    if len(instances) == 1:
        return instances[0]

    target, _ = pick(([instance.name for instance in instances] + ["<= Back"]), "Select an Instance:")
    if target == "<= Back":
        return
    return instances[target]  # type: ignore


def status_manager(
    boto_session: Session | BotoEnhanced, instance: Instance, connecting: bool = False, stopping: bool = False
) -> None | bool:
    """Manage Instance state. Set :param:`connecting` to True to automatically prepare the Instance for connection."""
    status = get_instance_status(boto_session, instance)

    # If stopping, wait for it to be stopped
    if status == "stopping":
        LOGGER.info("Waiting for the Instance to stop...")
        while status != "stopped":
            time.sleep(15)
            status = get_instance_status(boto_session, instance)
        time.sleep(15)

    # If stopped, ask user if they want to start
    if status == "stopped":
        if connecting:
            if not start_instance(boto_session, instance):
                return False
        elif stopping:
            return True
        else:
            opt, _ = pick(["Start", "<= Back"], "The Instance is stopped. What would you like to do?")
            if opt == "<= Back":
                return
            elif opt == "Start":
                start_instance(boto_session, instance)
        status = "pending"

    # If pending, wait for it to be running
    if status == "pending":
        LOGGER.info("Waiting for the Instance to start...")
        while status != "running":
            time.sleep(15)
            status = get_instance_status(boto_session, instance)
        if connecting:
            time.sleep(60)

    # If running, allow user to stop or restart
    if status == "running":
        if connecting:
            return True
        elif stopping:
            return stop_instance(boto_session, instance)

        opt, _ = pick(["Stop", "Restart", "<= Back"], "The Instance is running. What would you like to do?")
        if opt == "<= Back":
            return
        elif opt == "Stop":
            return stop_instance(boto_session, instance)
        elif opt == "Restart":
            stop_instance(boto_session, instance)
            # Wait for it to be stopped before starting again
            while status != "stopped":
                time.sleep(15)
                status = get_instance_status(boto_session, instance)
            time.sleep(15)
            return start_instance(boto_session, instance)
