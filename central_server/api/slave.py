from functools import partial
from typing import List, Dict, Tuple, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from central_server.models.check_in import CheckIn, CheckInStatus
from central_server.models.temp_log import TempLog, EventType
from central_server.models.room import Room
from central_server.core import MyScheduler
from central_server.core.queue import Service, ServiceStatus


from .conn_manager import MyManager


def add_slave_routes(app: FastAPI):
    async def hello(check_in_id: int, data: dict):
        pass

    async def slave_status_report(check_in_id: int, data: dict):
        check_in = CheckIn.get(check_in_id)
        cur_temp, tar_temp, mode, speed = [data[x] for x in ['cur_temp', 'tar_temp', 'mode', 'speed']]

        if check_in_id in pending_checkins:
            # add to scheduler's ready queue
            MyScheduler.req_queue.push(
                Service(
                    room_id=check_in.room_id, wind_speed=speed,
                    status=ServiceStatus.Waiting, time=MyScheduler.now()))
            pending_checkins.remove(check_in_id)

        room = Room.get(check_in.room_id)
        room.set.current_temp(cur_temp)
        room.set.target_temp(tar_temp)
        room.set.wind_mode(mode)
        room.set.wind_speed(mode)

    # 待就绪状态下的入住房间，这些入住记录有如下特征：
    #   1. 已经上线并且完成了身份验证
    #   2. 尚未进行第一次状态汇报，因而还未就绪送风
    pending_checkins: Set[int] = set()

    HANDLE_DICT = lambda check_in_id: {
        0: partial(hello, check_in_id),
        7: partial(slave_status_report, check_in_id)
    }

    async def slave_online(check_in_id: int):
        check_in = CheckIn.get(check_in_id)
        await TempLog.new(room_id=check_in.room_id, timestamp=MyScheduler.now(), event_type=EventType.ONLINE)

    async def slave_offline(check_in_id: int):
        check_in = CheckIn.get(check_in_id)
        await TempLog.new(room_id=check_in.room_id, timestamp=MyScheduler.now(), event_type=EventType.OFFLINE)

    async def distribute(check_in_id: int, message: dict):
        await HANDLE_DICT(check_in_id)[message['event_id']](message['data'])

    async def send_status(check_in_id: int):
        ws = MyManager.active_connections[check_in_id]
        data = {'mode': MyScheduler.wind_mode.value, 'temp': MyScheduler.temperature}
        await ws.send_json({
            'event_id': 1,
            'data': data
        })

    @app.websocket('/')
    async def handle_message(ws: WebSocket, room_id: str, user_id: str):
        check_in = await CheckIn.check(room_id=room_id, user_id=user_id, status=CheckInStatus.CheckIn)
        if check_in is None:
            # 有内鬼，终止交易！
            return
        await MyManager.connect(ws, check_in.id)
        await send_status(check_in.id)
        await slave_online(check_in.id)  # 记录 ONLINE 事件
        pending_checkins.add(check_in.id)
        try:
            while True:
                message = await ws.receive_json()
                await distribute(check_in, message)
        except WebSocketDisconnect:
            MyManager.disconnect(ws, check_in.id)
            await slave_offline(check_in.id)  # 记录 OFFLINE 事件
            if check_in.id in pending_checkins:
                pending_checkins.remove(check_in.id)
            MyScheduler.req_queue.remove_if_exists(check_in.room_id)
