from enum import Enum
from typing import NamedTuple


class AdminStatus(Enum):
    Off = 1
    On = 2


class Admin(NamedTuple):
    username: str
    password: str
    status: AdminStatus

    @staticmethod
    def get(username: str) -> 'Admin':
        pass

    @staticmethod
    def auth(username: str, password: str) -> 'Admin':
        pass

    @staticmethod
    def register(username: str, password: str) -> 'Admin':
        pass
