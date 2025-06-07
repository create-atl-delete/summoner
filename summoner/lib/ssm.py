import json
import logging
import shutil
import subprocess
from threading import Event, Thread

from summoner.lib.boto import BotoEnhanced, get_sessions, start_session, terminate_sessions
from summoner.lib.instance import Instance

LOGGER = logging.getLogger()


class DummySubprocess:
    def poll(self):
        return

    def kill(self):
        return


class SSMPlugin:
    def __init__(self, boto_session: BotoEnhanced, target: Instance) -> None:
        self.boto_session = boto_session
        self.target = target

        self.ssm_plugin_process = DummySubprocess()
        self.ready_for_connection = Event()
        self.stopped_by_user = Event()
        self.ssm_sessions = []

    def is_ready(self):
        return self.ready_for_connection.wait(15)

    def is_running(self):
        return self.ssm_plugin_process.poll() is None

    def stop(self):
        self.stopped_by_user.set()
        self.ssm_plugin_process.kill()
        terminate_sessions(self.boto_session, self.target, self.ssm_sessions)

    def start(self):

        def ssm_plugin_thread():
            while True:
                # Clean up any existing SSM sessions to same instance existing sessions
                existing_sessions = get_sessions(self.boto_session, self.target)
                if existing_sessions:
                    self.ssm_sessions.append(existing_sessions)
                    terminate_sessions(self.boto_session, self.target, self.ssm_sessions)

                if not (ssm_session := start_session(self.boto_session, self.target)):
                    return
                self.ssm_sessions.append(ssm_session)

                # Build cmd to run session-manager-plugin in subprocess.
                # Refer to, https://github.com/aws/session-manager-plugin/blob/mainline/src/sessionmanagerplugin/session/session.go
                cmd = [
                    shutil.which("session-manager-plugin"),
                    json.dumps(self.ssm_sessions[-1]),
                    self.target.region,
                    "StartSession",
                    self.boto_session.profile_name,
                    json.dumps({"Target": self.target.instance_id}),
                    f"https://ssm.{self.target.region}.amazonaws.com",
                ]
                LOGGER.debug(f"SSM plugin command set to:\n{cmd}")

                with subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                ) as self.ssm_plugin_process:
                    for line in self.ssm_plugin_process.stdout:  # type: ignore
                        LOGGER.debug(f"session-manager-plugin: {line.rstrip()}")
                        if "Cannot perform start session" in line:
                            LOGGER.error("Could not start SSM plugin.")
                        elif "Waiting for connections" in line:
                            self.ready_for_connection.set()

                if self.stopped_by_user.is_set():
                    break
                LOGGER.warning("SSM Plugin stopped unexpectedly. Restarting...")
                self.ready_for_connection.clear()

        ssm_plugin = Thread(name="ssm_plugin_thread", target=ssm_plugin_thread)
        ssm_plugin.daemon = True
        ssm_plugin.start()
