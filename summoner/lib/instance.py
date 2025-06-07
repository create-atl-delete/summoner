from random import randint

from summoner.conf.connection_types import CONNECTION_TYPES


class Instance:
    connection_types = CONNECTION_TYPES

    def __init__(
        self,
        name: str,
        region: str,
        instance_id: str,
        connection_type: str,
        domain: str | None = None,
        username: str | None = None,
        local_port: int | None = None,
    ):
        self.name = name
        self.region = region
        self.instance_id = instance_id
        self.connection_type = connection_type
        self.domain = domain
        self.username = username
        self.local_port = local_port or randint(50000, 60000)

        self.remote_port = self.connection_types[connection_type]  # type: ignore

    @classmethod
    def add_connection_type(cls, name: str, port: int):
        cls.connection_types.update({name: port})
