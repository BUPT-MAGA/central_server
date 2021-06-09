from time import time
from config import *
from central_server.models import WindMode, Room, CheckInStatus, TempLog, EventType, CheckIn, CenterStatus
from .queue import Queue


class Scheduler:
    def __init__(self):
        # set default mode
        self.req_queue = Queue(REQ_EXPIRED_TIME, MAX_SERVING_LEN)

    def turn_on(self):
        self._wind_mode = WindMode.Snow
        # self._timestamp = 0
        self._temperature = TEMP_DEFAULT[self._wind_mode]
        self._status = CenterStatus.Off
        self.req_queue.clear()

    async def tick(self):
        # self._timestamp += 1
        if self._status == CenterStatus.Off:
            return
        checkin_rooms = await Room.get_all(status=CheckInStatus.CheckIn)
        for room in checkin_rooms:
            if self.req_queue.is_serving(room.id):
                new_fee = UNIT_PRICE*PRICE_TABLE[room.wind_speed]/60
            else:
                new_fee = 0.0
            await TempLog.new(room_id=room.id,
                              wind_speed=room.wind_speed,
                              timestamp=int(time()),
                              event_type=EventType.TEMP,
                              current_temp=room.current_temp,
                              current_fee=new_fee
                              )
            check_in: CheckIn = await CheckIn.get_last(room_id=room.id, status=CheckInStatus.CheckIn)
            assert check_in is not None
            await CheckIn.set.fee(check_in.fee + new_fee)
        self.req_queue.tick()

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

    @temperature.setter
    def temperature(self, temp: int):
        if temp in TEMP_RANGE[self._wind_mode]:
            self._temperature = temp
        else:
            raise ValueError('Illegal temp value!')

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if isinstance(status, CenterStatus):
            if self._status != status:
                self._status = status
                if self._status == CenterStatus.On:
                    self.turn_on()
        else:
            raise ValueError('Illegal center status value!')
