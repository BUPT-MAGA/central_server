from typing import NamedTuple
from .room import WindSpeed


class TempLog(NamedTuple):
    checkin_id: int
    wind_speed: WindSpeed
    timestamp: str

    @staticmethod
    def add(checkin_id: int, wind_speed: WindSpeed, timestamp: str) -> 'TempLog':
        pass
