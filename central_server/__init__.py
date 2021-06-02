from fastapi import FastAPI
from central_server.api.center import add_center_routes
from central_server.api.slave import add_slave_routes

def create_app():
    app = FastAPI()
    add_center_routes(app)
    add_slave_routes(app)
    return app
