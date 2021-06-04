from enum import Enum
from typing import NamedTuple, Optional, Any

class CheckInStatus(Enum):
    CheckIn = 1
    CheckOut = 2

class CheckIn(NamedTuple):
    # Check in record id
    id: int
    # User ID (ID card number)
    user_id: str
    # Room ID
    room_id: str
    # Check in status (check in or check out)
    status: CheckInStatus
    checkin_time: str
    checkout_time: Optional[str]
    # Current fee
    fee: float

    @staticmethod
    def get(checkin_id: int) -> 'CheckIn':
        pass

    @staticmethod
    def create(user_id: str, room_id: str, now: str) -> 'CheckIn':
        pass

    @staticmethod
    def update(user_id: str, room_id: str, now: str) -> 'CheckIn':
        # check out
        pass

    @staticmethod
    def check(user_id: str, room_id: str, status: CheckInStatus) -> bool:
        pass
