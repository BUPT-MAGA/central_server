from enum import Enum
from pydantic import BaseModel
from .data_model import DataModel
from .types import AdminStatus


@DataModel(pkey_field='username')
class Admin(BaseModel):
    username: str
    password: str
    status: AdminStatus = AdminStatus.On

    @staticmethod
    async def check(username: str, password: str):
        return await Admin.get_first(username=username, password=password)
