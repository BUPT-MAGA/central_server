from functools import partial
from typing import List, Dict, Tuple, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from central_server.models.check_in import CheckIn, CheckInStatus
from central_server.models.temp_log import TempLog, EventType
from central_server.models.room import Room
from central_server.core import MyScheduler
from central_server.core.queue import Service, ServiceStatus
from central_server.reporting import slave_api

from .conn_manager import MyManager


def add_slave_routes(app: FastAPI):
    async def hello(check_in_id: int, data: dict):
        pass

    async def slave_status_report(check_in_id: int, data: dict):
        slave_api.info(f'<<- status report {check_in_id}: {data}')
        check_in: CheckIn = await CheckIn.get(check_in_id)
        cur_temp, tar_temp, mode, speed = [data[x] for x in ['cur_temp', 'tar_temp', 'mode', 'speed']]

        # if check_in_id in pending_checkins:
        #     # add to scheduler's ready queue
        #     MyScheduler.pending_queue.append(check_in_id)
        #     slave_api.info(f'pushing check in to scheduler')
        #     # MyScheduler.req_queue.push(
        #     #     Service(
        #     #         room_id=check_in.room_id, wind_speed=speed,
        #     #         status=ServiceStatus.Waiting, time=MyScheduler.now()))
        #     pending_checkins.remove(check_in_id)

        room = await Room.get(check_in.room_id)
        if room is None:
            slave_api.error(f'invalid room id: {check_in.room_id}')
            return
        await room.set.current_temp(cur_temp)
        await room.set.target_temp(tar_temp)
        if mode in {0, 1}:
            if not MyScheduler.exists(check_in_id):
                MyScheduler.add(check_in_id)
                await TempLog.new(room_id=check_in.room_id,
                                  wind_speed=room.wind_speed,
                                  timestamp=MyScheduler.now(),
                                  event_type=EventType.START,
                                  current_temp=room.current_temp,
                                  current_fee=check_in.fee)

            await room.set.wind_mode(mode)
        else:
            if MyScheduler.exists(check_in_id):
                await TempLog.new(room_id=check_in.room_id,
                                  wind_speed=room.wind_speed,
                                  timestamp=MyScheduler.now(),
                                  event_type=EventType.END,
                                  current_temp=room.current_temp,
                                  current_fee=check_in.fee)
            MyScheduler.remove_if_exists(check_in_id)
            # if check_in_id not in pending_checkins:
            #     pending_checkins.add(check_in_id)
            #     MyScheduler.remove_if_exists(check_in_id)
        await room.set.wind_speed(speed)

    # ????????????????????????????????????????????????????????????????????????
    #   1. ???????????????????????????????????????
    #   2. ????????????????????????????????????????????????????????????
    # pending_checkins: Set[int] = set()

    HANDLE_DICT = lambda check_in_id: {
        0: partial(hello, check_in_id),
        7: partial(slave_status_report, check_in_id)
    }

    async def slave_online(check_in_id: int):
        check_in = await CheckIn.get(check_in_id)
        await TempLog.new(room_id=check_in.room_id, timestamp=MyScheduler.now(), event_type=EventType.ONLINE)

    async def slave_offline(check_in_id: int):
        check_in = await CheckIn.get(check_in_id)
        await TempLog.new(room_id=check_in.room_id, timestamp=MyScheduler.now(), event_type=EventType.OFFLINE)

    async def distribute(check_in_id: int, message: dict):
        if message['event_id'] not in {0, 7}:
            return
        await HANDLE_DICT(check_in_id)[message['event_id']](message['data'])

    async def send_status(check_in_id: int):
        ws = MyManager.active_connections[check_in_id]
        data = {'mode': MyScheduler.wind_mode.value, 'temp': MyScheduler.temperature}
        slave_api.info(f'->> sending status {check_in_id}, data = {data}')
        await ws.send_json({
            'event_id': 1,
            'data': data
        })

    async def send_interval(check_in_id: int):
        ws = MyManager.active_connections[check_in_id]
        # FIXME use config.WORK_RATE
        data = {'interval': 1000}
        slave_api.info(f'->> sending interval {check_in_id}, data = {data}')
        await ws.send_json({
            'event_id': 6,
            'data': data
        })

    @app.websocket('/ws/')
    async def handle_message(ws: WebSocket, room_id: str, user_id: str):
        slave_api.info(f'<-> new connection with room_id={room_id}, user_id={user_id}')
        check_in = await CheckIn.check(room_id=room_id, user_id=user_id, status=CheckInStatus.CheckIn)
        if check_in is None:
            slave_api.warn(f'<-> invalid check in, refuse to connect')
            # ???????????????????????????
            return
        if check_in.id in MyManager.active_connections:
            prev_ws = MyManager.active_connections[check_in.id]
            await prev_ws.close()
        await MyManager.connect(ws, check_in.id)
        slave_api.info(f'<-> valid authorization, connected: room_id={room_id}, user_id={user_id}, check in {check_in.id}')
        await send_status(check_in.id)
        await send_interval(check_in.id)
        await slave_online(check_in.id)  # ?????? ONLINE ??????
        # pending_checkins.add(check_in.id)
        MyScheduler.pending_queue.append(check_in.id)
        try:
            while True:
                message = await ws.receive_json()
                # slave_api.info(f'receive message from {check_in.id}: {message}')
                await distribute(check_in.id, message)
        except WebSocketDisconnect as e:
            print(e)
            MyManager.disconnect(ws, check_in.id)
            await slave_offline(check_in.id)  # ?????? OFFLINE ??????
            # if check_in.id in pending_checkins:
            #     pending_checkins.remove(check_in.id)
            MyScheduler.remove_if_exists(check_in.id)
            slave_api.info(f'<-> check in {check_in.id} disconnected')
            # MyScheduler.req_queue.remove_if_exists(check_in.room_id)
