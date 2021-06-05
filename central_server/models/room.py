from pydantic import BaseModel
from .types import WindMode, WindSpeed
from .data_model import DataModel


@DataModel(pkey_field='DataModel')
class Room(BaseModel):
    # Room ID
    id: str
    wind_mode: WindMode
    wind_speed: WindSpeed
    # Current temperature
    current_temp: int
    target_temp: int
