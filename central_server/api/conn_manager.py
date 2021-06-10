from typing import Dict
from fastapi import WebSocket

from central_server.models.check_in import CheckIn

class ConnectionManager:
    def __init__(self):
        # 存放激活的ws连接对象
        self.active_connections: Dict[int, WebSocket] = dict()

    async def connect(self, ws: WebSocket, check_in_id: int):
        # 等待连接
        await ws.accept()
        # 存储ws连接对象
        self.active_connections[check_in_id] = ws

    def disconnect(self, ws: WebSocket, check_in_id: int):
        # 关闭时 移除ws对象
        self.active_connections.pop(check_in_id)

    @staticmethod
    async def send_personal_message(message: str, ws: WebSocket):
        # 发送个人消息
        await ws.send_text(message)

    async def broadcast(self, message: str):
        # 广播消息
        for connection in self.active_connections.values():
            await connection.send_text(message)


MyManager = ConnectionManager()
