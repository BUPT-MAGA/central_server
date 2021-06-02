from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        # 存放激活的ws连接对象
        self.active_connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        # 等待连接
        await ws.accept()
        # 存储ws连接对象
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        # 关闭时 移除ws对象
        self.active_connections.remove(ws)

    @staticmethod
    async def send_personal_message(message: str, ws: WebSocket):
        # 发送个人消息
        await ws.send_text(message)

    async def broadcast(self, message: str):
        # 广播消息
        for connection in self.active_connections:
            await connection.send_text(message)

def add_slave_routes(app: FastAPI):
    async def hello(data: dict):
        pass

    HANDLE_LIST = [
        hello
    ]

    async def distribute(message: dict):
        await HANDLE_LIST[message['event_id']](message['data'])

    manager = ConnectionManager()
    @app.websocket('/')
    async def handle_message(ws: WebSocket):
        await manager.connect(ws)
        await manager.broadcast(f'new air come in!')
        try:
            while True:
                message = await ws.receive_json()
                await distribute(message)
                await ws.send_text('hello')
        except WebSocketDisconnect:
            manager.disconnect(ws)
            await manager.broadcast(f"a air leaves")
