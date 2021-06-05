from enum import Enum
from typing import NamedTuple, Optional, Any
from pydantic import BaseModel
from .types import CheckInStatus
from .data_model import DataModel


@DataModel(pkey_field='id')
class CheckIn(BaseModel):
    # Check in record id
    id: int
    # User ID (ID card number)
    user_id: str
    # Room ID
    room_id: str
    # Check in status (check in or check out)
    status: CheckInStatus
    checkin_time: int
    checkout_time: Optional[int]
    # Current fee
    fee: float
