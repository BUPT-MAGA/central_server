from flask import Flask
from flask_socketio import SocketIO
from central_server.api.center import add_center_routes
from central_server.api.slave import add_slave_routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    add_center_routes(app)
    socketio = SocketIO(app)
    add_slave_routes(socketio)
    return app, socketio
