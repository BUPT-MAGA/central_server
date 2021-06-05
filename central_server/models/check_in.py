from enum import Enum
from typing import NamedTuple, Optional, Any
from pydantic import BaseModel
from .types import CheckInStatus
from .data_model import DataModel


@DataModel(pkey_field='id', auto_inc=True)
class CheckIn(BaseModel):
    # Check in record id
    id: int
    # User ID (ID card number)
    user_id: str
    # Room ID
    room_id: str
    # Check in status (check in or check out)
    status: CheckInStatus = CheckInStatus.CheckIn
    checkin_time: int
    checkout_time: Optional[int] = None
    # Current fee
    fee: float = 0.0


    @staticmethod
    async def check(room_id: str, user_id: str, status: CheckInStatus):
        res = await CheckIn.get_first(room_id=room_id, user_id=user_id, status=status)
        return res
