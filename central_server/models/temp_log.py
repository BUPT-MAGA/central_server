from typing import NamedTuple, Optional
from enum import Enum
from .room import WindSpeed

class EventType(Enum):
    TEMP = 1
    START = 2
    END = 3

class TempLog(NamedTuple):
    checkin_id: int
    wind_speed: Optional[WindSpeed]
    timestamp: str
    event_type: EventType

    @staticmethod
    def add(checkin_id: int, wind_speed: WindSpeed, timestamp: str) -> 'TempLog':
        pass
