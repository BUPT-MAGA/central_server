from enum import Enum
from typing import NamedTuple
from pydantic import BaseModel


class WindMode(Enum):
    Snow = 1
    Sun = 2


class WindSpeed(Enum):
    Low = 1
    Mid = 2
    High = 3


class Room(BaseModel):
    # Room ID
    id: str
    wind_mode: WindMode
    wind_speed: WindSpeed
    # Current temperature
    current_temp: int
    target_temp: int

    @staticmethod
    def get(room_id: str) -> 'Room':
        pass
