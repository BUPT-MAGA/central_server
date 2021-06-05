from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from central_server.api.center import add_center_routes
from central_server.api.slave import add_slave_routes
from central_server.core import MyScheduler
from config import *

def create_app():
    app = FastAPI()
    add_center_routes(app)
    add_slave_routes(app)

    @app.on_event('startup')
    @repeat_every(seconds=REAL_SEC_PER_MIN, wait_first=True)
    async def periodic():
        await MyScheduler.tick()

    return app
