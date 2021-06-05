from enum import Enum
from pydantic import BaseModel
from .data_model import DataModel
from .types import AdminStatus


@DataModel(pkey_field='username')
class Admin(BaseModel):
    username: str
    password: str
    status: AdminStatus
