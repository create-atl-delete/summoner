import logging
from datetime import datetime
from time import time
from typing import List

import pytz
from boto3 import Session
from botocore import exceptions
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

from summoner.lib.decorators import method_decorator
from summoner.lib.instance import Instance

LOGGER = logging.getLogger()

SSM_ERRORS = ["TargetNotConnected", "InternalServerError"]
PERMISSION_ERRORS = ["AccessDenied", "UnauthorizedOperation", "403"]
RESOURCE_ERRORS = ["ResourceNotFoundException", "InvalidInstanceID"]
STATE_ERRORS = ["IncorrectInstanceState"]


class BotoEnhancedException(Exception):
    def __init___(self, message=None):
        super().__init__(message)


def boto_wrapper(_):
    def outer(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (exceptions.ClientError, exceptions.BotoCoreError) as ex:
                if any(error_string in str(ex) for error_string in RESOURCE_ERRORS):
                    LOGGER.exception("Instance could not be found.")
                    return
                elif any(error_string in str(ex) for error_string in PERMISSION_ERRORS):
                    LOGGER.exception(f"You do not have permission to interact with that Instance. Error: {ex}")
                    return
                elif any(error_string in str(ex) for error_string in STATE_ERRORS):
                    LOGGER.exception("Instane state could not be changed. Please try again in a few minutes.")
                    return
                elif any(error_string in str(ex) for error_string in SSM_ERRORS):
                    LOGGER.exception(f"Could not start SSM session. Error: {ex}")
                    return
                raise BotoEnhancedException(f"Unandled exception: {ex}")

        return inner

    return outer


class BotoEnhanced(Session):
    def __init__(
        self,
        region_name: str,
        profile_name: str,
        sts_arn: str | None = None,
        session_name: str | None = None,
        session_ttl: int = 3600,
    ):
        self.region_name = region_name  # type: ignore
        self.profile_name = profile_name  # type: ignore
        self.sts_arn = sts_arn
        self.session_name = session_name or self.__class__.__name__
        self.session_ttl = session_ttl

        try:
            super().__init__(region_name=self.region_name, profile_name=self.profile_name)
        except exceptions.ProfileNotFound:
            raise Exception(f"Could not find '{profile_name}' profile in AWS config.")
        self.refreshable_session()

    def __get_session_credentials(self):
        if self.sts_arn:
            sts_client = super().client("sts", region_name=self.region_name)
            response = sts_client.assume_role(
                RoleArn=self.sts_arn,
                RoleSessionName=self.session_name,
                DurationSeconds=self.session_ttl,
            ).get("Credentials")

            credentials = {
                "access_key": response.get("AccessKeyId"),
                "secret_key": response.get("SecretAccessKey"),
                "token": response.get("SessionToken"),
                "expiry_time": response.get("Expiration").isoformat(),
            }
        else:
            session_credentials = super().get_credentials().get_frozen_credentials()
            credentials = {
                "access_key": session_credentials.access_key,
                "secret_key": session_credentials.secret_key,
                "token": session_credentials.token,
                "expiry_time": datetime.fromtimestamp(time() + self.session_ttl).replace(tzinfo=pytz.utc).isoformat(),
            }

        return credentials

    def refreshable_session(self):
        session = get_session()
        session._credentials = RefreshableCredentials.create_from_metadata(
            metadata=self.__get_session_credentials(),
            refresh_using=self.__get_session_credentials,
            method="sts-assume-role",
        )
        session.set_config_variable("region", self.region_name)
        super().__init__(botocore_session=session)

    def client(self, *args, **kwargs):
        client = super().client(*args, **kwargs)
        return method_decorator(boto_wrapper)(client)

    def resource(self, *args, **kwargs):
        resource = super().resource(*args, **kwargs)
        return method_decorator(boto_wrapper)(resource)


def get_instance_status(boto_session: Session | BotoEnhanced, instance: Instance) -> None | str:
    ec2_client = boto_session.client("ec2", region_name=instance.region)
    response = ec2_client.describe_instance_status(InstanceIds=[instance.instance_id])
    try:
        return response["InstanceStatuses"][0]["InstanceState"]["Name"]
    except IndexError:
        return "stopped"


def start_instance(boto_session: Session | BotoEnhanced, instance: Instance):
    LOGGER.info(f"Starting Instance {instance.name}...")
    ec2_client = boto_session.client("ec2", region_name=instance.region)
    ec2_client.start_instances(InstanceIds=[instance])


def stop_instance(boto_session: Session | BotoEnhanced, instance: Instance):
    LOGGER.info(f"Stopping Instance {instance.name}..")
    ec2_client = boto_session.client("ec2", region_name=instance.region)
    ec2_client.stop_instances(InstanceIds=[instance])


def get_sessions(boto_session: Session | BotoEnhanced, instance: Instance) -> List[str]:
    ssm_client = boto_session.client("ssm", region_name=instance.region)
    response = ssm_client.describe_sessions(State="Active", Filters=[{"key": "Target", "value": instance.instance_id}])

    ssm_sessions = []
    if "Sessions" in response:
        for session in response["Sessions"]:
            ssm_sessions.append(session)
    return ssm_sessions


def start_session(boto_session: Session | BotoEnhanced, instance: Instance) -> str | None:
    ssm_client = boto_session.client("ssm", region_name=instance.region)
    return ssm_client.start_session(
        Target=instance,
        DocumentName="AWS-StartPortForwardingSession",
        Reason="Summoner Session",
        Parameters={
            "portNumber": [str(instance.remote_port)],
            "localPortNumber": [str(instance.local_port)],
        },
    )


def terminate_sessions(boto_session: Session | BotoEnhanced, instance: Instance, ssm_sessions: List[str]):
    ssm_client = boto_session.client("ssm", region_name=instance.region)
    for session in ssm_sessions:
        ssm_client.terminate_session(SessionId=session["SessionId"])  # type: ignore
