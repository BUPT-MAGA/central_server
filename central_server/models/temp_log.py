from typing import NamedTuple, Optional
from enum import Enum
from .room import WindSpeed
from pydantic import BaseModel
from .data_model import DataModel
from .types import EventType


@DataModel(pkey_field='id', auto_inc=True)
class TempLog(BaseModel):
    id: int
    wind_speed: Optional[WindSpeed]
    timestamp: str
    event_type: EventType
    initial_temp: int
    current_temp: int
