from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from central_server.api.center import add_center_routes
from central_server.api.slave import add_slave_routes
from config import *

def create_app():
    app = FastAPI()
    add_center_routes(app)
    add_slave_routes(app)

    @app.on_event('start_up')
    @repeat_every(seconds=REAL_SEC_PER_MIN)
    def periodic():
        pass

    return app
