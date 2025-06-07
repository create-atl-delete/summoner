import logging
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

from summoner.conf.connection_types import CONNECTION_TYPES
from summoner.lib.const import SUMMONER_FOLDER
from summoner.summoner import Summoner

LOGGER = logging.getLogger()


def get_args():
    parser = ArgumentParser(
        prog="Summoner",
        description="A lightweight VDI-like client for AWS SSM",
    )
    subparser = parser.add_subparsers(dest="mode", required=True)

    config = subparser.add_parser(
        "config", description="Load an account config file containing profile and Instance info."
    )
    config.add_argument(
        "-a",
        "--account",
        help="Account config file to load.",
        dest="config_file",
        type=str,
        default="default",
    )

    select = subparser.add_parser("select", description="Select an Instance in the UI.")
    select.add_argument(
        "-a",
        "--aws_profile",
        help="AWS Profile name.",
        dest="aws_profile",
        type=str,
        required=True,
    )
    select.add_argument(
        "-r",
        "--region",
        help="AWS Region the Instance in.",
        dest="region",
        type=str,
        required=True,
    )

    instance = subparser.add_parser("instance", description="Provide profile and Instance details as CLI args.")
    instance.add_argument(
        "-a",
        "--aws_profile",
        help="AWS Profile name.",
        dest="aws_profile",
        type=str,
        required=True,
    )
    instance.add_argument(
        "-r",
        "--region",
        help="AWS Region the Instance is in.",
        dest="region",
        type=str,
        required=True,
    )
    instance.add_argument(
        "-i",
        "--instance_id",
        help="Instance ID.",
        dest="instance_id",
        type=str,
        required=True,
    )
    instance.add_argument(
        "-c",
        "--connection_type",
        help="Connection type.",
        choices=CONNECTION_TYPES.keys(),
        dest="connection_type",
        type=str,
        required=True,
    )
    instance.add_argument(
        "-p",
        "--port",
        help="Local port number to forward.",
        dest="port",
        default=None,
        type=int,
    )
    instance.add_argument(
        "-d",
        "--domain",
        help="Domain.",
        dest="domain",
        default=None,
        type=str,
    )
    instance.add_argument(
        "-u",
        "--username",
        help="Username.",
        dest="username",
        default=None,
        type=str,
    )

    parser.add_argument(
        "-l",
        "--log_lvl",
        help="Set logging level to DEBUG.",
        action="store_const",
        dest="log_lvl",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="1",
    )
    return parser.parse_args()


def menu_wrapper(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            LOGGER.exception("Keyboard interupt received.")
            sys.exit(1)
        except Exception as ex:
            LOGGER.exception(ex)
            time.sleep(3)

    return inner


@menu_wrapper
def main():
    args_dict = dict(get_args()._get_kwargs())

    logging.basicConfig(
        level=args_dict.pop("log_lvl"),
        format=f"%(acstime)s | %(message)s",
        handlers=[logging.FileHandler(Path(SUMMONER_FOLDER, "log"), "w"), logging.StreamHandler()],
    )

    Summoner(**args_dict)
    sys.exit(0)


if __name__ == "__main__":
    main()
