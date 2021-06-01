from flask import Flask, request
from flask_socketio import SocketIO, send, emit
import json

def add_slave_routes(socketio: SocketIO):
    def hello(data: dict):
        return 'hello'

    HANDLER_DICT = [
        hello
    ]

    @socketio.on('message')
    def handle_message(message):
        message = json.loads(message)
        return HANDLER_DICT[message['event_id']](message['data'])
