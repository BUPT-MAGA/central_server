from enum import Enum
from typing import NamedTuple, Optional, List
from pydantic import BaseModel
from .my_types import CheckInStatus
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
    async def check(**kwargs):
        res = await CheckIn.get_first(**kwargs)
        return res

    @staticmethod
    async def get_bill(user_id: str):
        check_ins: List[CheckIn] = await CheckIn.get_all(user_id=user_id)
        if len(check_ins) == 0:
            return None
        ret = []
        for check_in in check_ins:
            bill = {}
            bill['room_id'] = check_in.room_id
            bill['status'] = check_in.status
            bill['checkin_time'] = check_in.checkin_time
            if check_in.status == CheckInStatus.CheckOut:
                bill['checkout_time'] = check_in.checkout_time
            bill['fee'] = check_in.fee
            ret.append(bill)
        return ret
