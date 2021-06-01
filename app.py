from flask import Flask
from flask_socketio import SocketIO
from central_server import create_app

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app)
