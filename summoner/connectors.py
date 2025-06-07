import logging
import shutil
import subprocess
import sys
import time
from pathlib import Path

from summoner.evocation import Evocation
from summoner.lib.const import RDP_TEMPLATE, SUMMONER_FOLDER, VNC_TEMPLATE
from summoner.lib.instance import Instance

LOGGER = logging.getLogger()


def rdp_connection(target: Instance, **kwargs):
    full_username = f"{target.domain}\\{target.username}" if target.domain else target.username

    rdp_file = Path(SUMMONER_FOLDER, f"{target.name}.rdp")
    if not rdp_file.exists():
        shutil.copyfile(RDP_TEMPLATE.as_posix(), rdp_file.as_posix())

    # Format RDP file for this run
    with open(rdp_file, "r", encoding="utf-16") as f0:
        with open("this.rdp", "w", encoding="utf-16") as f1:
            f1.write(f0.read().format(full_username=full_username, local_port=target.local_port))

    print(
        "Launching RDP client..."
        f"\nIf the client fails to start or you would like to use a different one, connect to localhost: {target.local_port} as {full_username}."
    )

    launcher = "Start-Process" if sys.platform == "win32" else "open"
    if subprocess.run([launcher, "this.rdp"]).returncode != 0:
        LOGGER.error("No default app found for .rdp files. Please set one and try again.")


def ssh_connection(target: Instance, evocation: Evocation, **kwargs):
    ssh_target = f"{target.username}@localhost" if target.username else "localhost"

    print(
        "Dropping into SSH..."
        f"\nIf the client fails to start or you would like to use a different one, connect to {ssh_target}:{target.local_port}."
        "\nPlease do not close this terminal. Use 'exit' to end the session gracefully."
    )

    cmd = [
        "ssh",
        ssh_target,
        "-p",
        target.local_port,
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=no",
    ]
    # On Windows, run SSH in a new shell to avoid breaking STDOUT
    if sys.platform == "win32":
        cmd.insert(0, "powershell.exe")

    # SSH connection runs in a loop so it can be restarted if the ssm session drops
    while True:
        if subprocess.run(cmd).returncode != 0:
            # If ssm plugin is running, the failure to SSH was likely user error, so break
            if evocation.is_running():
                LOGGER.error("Could not connect via SSH. This could be due to incorrect credentials.")
                time.sleep(3)
                break
            # Otherwise, ssm should be busy restarting, so loop
            if not evocation.is_ready():
                break
        # SSH stopped gracefully, so break
        break


def vnc_connection(target: Instance, **kwargs):
    rdp_file = Path(SUMMONER_FOLDER, f"{target.name}.vnc")
    if not rdp_file.exists():
        shutil.copyfile(VNC_TEMPLATE.as_posix(), rdp_file.as_posix())

    # Format RDP file for this run
    with open(rdp_file, "r", encoding="utf-16") as f0:
        with open("this.vnc", "w", encoding="utf-16") as f1:
            f1.write(f0.read().format(local_port=target.local_port))

    print(
        "Launching VNC client..."
        f"\nIf the client fails to start or you would like to use a different one, connect to localhost: {target.local_port}."
    )

    launcher = "Start-Process" if sys.platform == "win32" else "open"
    if subprocess.run([launcher, "this.vnc"]).returncode != 0:
        LOGGER.error("No default app found for .vnc files. Please set one and try again.")
