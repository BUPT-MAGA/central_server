from pydantic import BaseModel
from .types import WindMode, WindSpeed, CheckInStatus
from .data_model import DataModel


@DataModel(pkey_field='id')
class Room(BaseModel):
    # Room ID
    id: str
    status: CheckInStatus
    wind_mode: WindMode
    wind_speed: WindSpeed
    # Current temperature
    current_temp: int
    target_temp: int
