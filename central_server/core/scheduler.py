from typing import Tuple, List
from collections import namedtuple
from time import time
from config import *
from central_server.models import WindMode, Room, CheckInStatus, TempLog, EventType, CheckIn, CenterStatus
from .queue import Queue
from central_server.api.conn_manager import MyManager


Serving = namedtuple('Serving', ['check_in_id', 'service_time'])


class Scheduler:

    def __init__(self):
        # set default mode
        # self.req_queue = Queue(REQ_EXPIRED_TIME, MAX_SERVING_LEN)
        self.init_air()

        self.pending_queue: List[int] = []
        self.serving_queue: List[Serving] = []

    async def split_pending_queue(self):
        async def need_speed(check_in_id: int) -> bool:
            check_in: CheckIn = await CheckIn.get(check_in_id)
            room: Room = await Room.get(check_in.id)
            if self.wind_mode == WindMode.Snow:
                return room.current_temp > room.target_temp
            else:
                return room.current_temp < room.target_temp

        ready = []
        pending = []
        for check_in_id in self.pending_queue:
            need = await need_speed(check_in_id)
            if need:
                ready.append(check_in_id)
            else:
                pending.append(check_in_id)
        return ready, pending

    def remove_if_exists(self, check_in_id: int):
        self.pending_queue = [x for x in self.pending_queue if x != check_in_id]
        self.serving_queue = [x for x in self.serving_queue if x.check_in_id != check_in_id]

    async def split_serving_queue(self):
        async def temp_satisfied(serving: Serving) -> bool:
            check_in: CheckIn = await CheckIn.get(serving.check_in_id)
            room: Room = await Room.get(check_in.id)
            if self.wind_mode == WindMode.Snow:
                return room.current_temp <= room.target_temp
            else:
                return room.current_temp >= room.target_temp

        async def swap_out(serving: Serving) -> bool:
            return serving.service_time >= REQ_EXPIRED_TIME

        async def should_drop(serving: Serving) -> bool:
            b1 = await temp_satisfied(serving)
            b2 = await swap_out(serving)

            return b1 or b2

        ok = []
        drop = []
        for serving in self.serving_queue:
            need_drop = await should_drop(serving)
            if need_drop:
                drop.append(serving)
            else:
                ok.append(serving)
        return ok, drop

    async def update_queue(self):
        pending_ready, pending_wait = await self.split_pending_queue()
        serving_ok, serving_drop = await self.split_serving_queue()

        capacity = self._max_serving_len - len(serving_ok)

        start_service = pending_ready[capacity:]
        end_service = [x.check_in_id for x in serving_drop]

        next_pending = pending_ready[capacity:] + pending_wait + [x.check_in_id for x in serving_drop]
        next_serving = serving_ok + [Serving(check_in_id=x, service_time=0) for x in pending_wait[:capacity]]

        self.pending_queue = next_pending
        self.serving_queue = next_serving

        return start_service, end_service

    async def is_serving(self, room_id: str):
        for serving in self.serving_queue:
            check_in_id = serving.check_in_id
            check_in = await CheckIn.get(check_in_id)
            if check_in.room_id == room_id:
                return True
        return False

    def init_air(self):
        self._status = CenterStatus.Off
        self._wind_mode = WindMode.Snow
        self._temperature = TEMP_DEFAULT[self._wind_mode]
        self._max_serving_len = MAX_SERVING_LEN
        self._unit_price = UNIT_PRICE
        # self.req_queue.clear()

    def now(self):
        return int(time())

    async def send_wind_status(self, check_in_id: int):
        check_in = await CheckIn.get(check_in_id)
        room_id = check_in.room_id
        room = await Room.get(room_id)
        temp = self.temperature
        speed = room.wind_speed
        mode = self.wind_mode
        cost = (await CheckIn.get(check_in.id)).fee
        data = {
            'temp': temp,
            'speed': speed,
            'mode': mode,
            'cost': cost
        }
        ws = MyManager.active_connections[check_in]
        await ws.send_json({
            'event_id': 3,
            'data': data
        })


    async def tick(self):
        if self._status == CenterStatus.Off:
            return

        start_service, end_service = await self.update_queue()
        for start_id in start_service:
            check_in: CheckIn = await CheckIn.get(start_id)
            room: Room = await Room.get(check_in.room_id)
            await TempLog.new(room_id=check_in.room_id,
                              wind_speed=None,
                              timestamp=self.now(),
                              event_type=EventType.START,
                              current_temp=room.current_temp,
                              current_fee=0.0)
        for end_id in end_service:
            check_in: CheckIn = await CheckIn.get(end_id)
            room: Room = await Room.get(check_in.room_id)
            await TempLog.new(room_id=check_in.room_id,
                              wind_speed=None,
                              timestamp=self.now(),
                              event_type=EventType.END,
                              current_temp=room.current_temp,
                              current_fee=0.0)

        for serving in self.serving_queue:
            check_in_id = serving.check_in_id
            await self.send_wind_status(check_in_id)

        checkin_rooms = await Room.get_all(status=CheckInStatus.CheckIn)
        for room in checkin_rooms:
            is_serving = self.is_serving(room.id)
            if is_serving:
                new_fee = self._unit_price*PRICE_TABLE[room.wind_speed]/60
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
        # self.req_queue.tick()

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
    def status(self, status: CenterStatus):
        if isinstance(status, CenterStatus):
            if self._status != status:
                self._status = status
                if self._status == CenterStatus.On:
                    self.init_air()
        else:
            raise ValueError('Illegal center status value!')

    @property
    def max_serving_len(self):
        return self._max_serving_len

    @max_serving_len.setter
    def max_serving_len(self, max_serving_len: int):
        if isinstance(max_serving_len, int) and max_serving_len > 0:
            self._max_serving_len = max_serving_len
        else:
            raise ValueError('Illegal max serving len!')

    @property
    def unit_price(self):
        return self._unit_price

    @unit_price.setter
    def unit_price(self, unit_price: float):
        if isinstance(unit_price, float) and unit_price > 0:
            self._unit_price = unit_price
        else:
            raise ValueError('Illegal unit price!')
