from pydantic import BaseModel
from typing import List
from .my_types import WindMode, WindSpeed, CheckInStatus
from .data_model import DataModel
from .check_in import CheckIn


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

    @staticmethod
    async def get_info():
        rooms: List[Room] = await Room.list_all()
        ret = []
        for room in rooms:
            info = {}
            info['room_id'] = room.id
            info['status'] = room.status
            if room.status == CheckInStatus.CheckIn:
                checkin: CheckIn = await CheckIn.get_last(room_id=room.id)
                try:
                    assert checkin.status == room.status
                except:
                    print('Incorrect join between Room and Checkin!')
                    print(checkin.status, room.status)
                    continue
                info['user_id'] = checkin.user_id
            ret.append(info)
        return ret

    @staticmethod
    async def get_status():
        rooms: List[Room] = await Room.list_all()
        return rooms
