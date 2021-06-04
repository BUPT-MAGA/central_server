import asyncio
from time import sleep
from config import REAL_SEC_PER_MIN, REQ_EXPIRED_TIME, MAX_SERVING_LEN, TEMP_RANGE, TEMP_DEFAULT
from central_server.models import WindMode
from .queue import Queue


class Scheduler:
    def __init__(self, wind_mode=WindMode.Snow):
        # set default mode
        self.wind_mode = wind_mode
        self.req_queue = Queue(REQ_EXPIRED_TIME, MAX_SERVING_LEN)
        self.timestamp = 0
        self.temprature = TEMP_DEFAULT[self.wind_mode]

    def loop(self):
        while True:
            sleep(REAL_SEC_PER_MIN)
            self.tick()

    def tick(self):
        self.timestamp += 1
        self.req_queue.tick()
