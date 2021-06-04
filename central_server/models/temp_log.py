from typing import NamedTuple, Optional
from enum import Enum
from .room import WindSpeed
from pydantic import BaseModel


class EventType(Enum):
    TEMP = 1
    START = 2
    END = 3


class TempLog(BaseModel):
    checkin_id: int
    wind_speed: Optional[WindSpeed]
    timestamp: str
    event_type: EventType
    initial_temp: int
    current_temp: int

    @staticmethod
    def add(checkin_id: int, wind_speed: WindSpeed, timestamp: str) -> 'TempLog':
        pass
