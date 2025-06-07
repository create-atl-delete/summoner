import logging
from typing import Callable

from summoner.lib.boto import BotoEnhanced
from summoner.lib.instance import Instance
from summoner.lib.ssm import SSMPlugin

LOGGER = logging.getLogger()


class Action:
    def __init__(self, func: Callable, **kwargs) -> None:
        self.func = func
        self.kwargs = kwargs


class Evocation(SSMPlugin):
    def __init__(self, boto_session: BotoEnhanced, instance: Instance):
        self.plugin = super().__init__(boto_session, instance)

    def connect(self, connect_func: Action):
        self.start()

        if self.is_ready():
            connect_func.func(evocation=self, **connect_func.kwargs)

        self.stop()
