from enum import Enum
from typing import NamedTuple
from pydantic import BaseModel


class AdminStatus(Enum):
    Off = 1
    On = 2


class Admin(BaseModel):
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

    @staticmethod
    def check(username: str) -> bool:
        pass
