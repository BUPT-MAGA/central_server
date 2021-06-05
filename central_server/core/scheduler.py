import asyncio
from time import sleep
from config import *
from central_server.models import WindMode, Room, CheckInStatus, TempLog, EventType, CheckIn
from .queue import Queue


class Scheduler:
    def __init__(self, wind_mode=WindMode.Snow):
        # set default mode
        self._wind_mode = wind_mode
        self.req_queue = Queue(REQ_EXPIRED_TIME, MAX_SERVING_LEN)
        self._timestamp = 0
        self._temperature = TEMP_DEFAULT[self._wind_mode]

    # async def loop(self):
    #     while True:
    #         await asyncio.sleep(REAL_SEC_PER_MIN)
    #         await self.tick()

    async def tick(self):
        self._timestamp += 1
        checkin_rooms = await Room.get_all(status=CheckInStatus.CheckIn)
        for room in checkin_rooms:
            await TempLog.new(wind_speed=room.wind_speed,
                              timestamp=self._timestamp,
                              event_type=EventType.TEMP,
                              current_temp=room.current_temp)
            check_in: CheckIn = await CheckIn.get_last(room_id=room.id, status=CheckInStatus.CheckIn)
            assert check_in is not None
            await CheckIn.set.fee(self.update_fee(check_in.fee, room))
        self.req_queue.tick()

    def update_fee(self, origin_fee: float, room: Room):
        if self.req_queue.is_serving(room.id):
            return origin_fee + UNIT_PRICE*PRICE_TABLE[room.wind_speed]
        return origin_fee

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def wind_mode(self):
        return self._wind_mode

    @wind_mode.setter
    def wind_mode(self, wind_mode: WindMode):
        if isinstance(wind_mode, WindMode):
            if self._wind_mode != wind_mode:
                self._wind_mode = wind_mode
                self._temperature = TEMP_DEFAULT[self._wind_mode]
        else:
            raise ValueError('Illegal wind mode value!')

    @property
    def temperature(self):
        return self._temperature
