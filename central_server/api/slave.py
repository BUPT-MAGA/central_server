from functools import partial
from typing import List, Dict, Tuple
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from central_server.models.check_in import CheckIn, CheckInStatus
from central_server.core import MyScheduler

from .conn_manager import MyManager

def add_slave_routes(app: FastAPI):
    async def hello(data: dict):
        pass

    HANDLE_DICT = {
        0: hello,
    }

    async def distribute(message: dict):
        await HANDLE_DICT[message['event_id']](message['data'])

    async def send_status(check_in: CheckIn):
        ws = MyManager.active_connections[check_in]
        await ws.send_json({'mode': MyScheduler.wind_mode.value, 'temp': MyScheduler.temperature})

    @app.websocket('/')
    async def handle_message(ws: WebSocket, room_id: str, user_id: str):
        check_in = await CheckIn.check(room_id=room_id, user_id=user_id, status=CheckInStatus.CheckIn)
        if check_in is None:
            # 有内鬼，终止交易！
            return
        await MyManager.connect(ws, check_in)
        await send_status(check_in)
        try:
            while True:
                message = await ws.receive_json()
                await distribute(message)
                await ws.send_text('hello')
        except WebSocketDisconnect:
            MyManager.disconnect(ws, check_in)
