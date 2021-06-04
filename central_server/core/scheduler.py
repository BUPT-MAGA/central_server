import asyncio
from central_server.models import WindMode


class Scheduler:
    def __init__(self, wind_mode=WindMode.Snow):
        # set default mode
        self.wind_mode = wind_mode

    async def loop(self):
        while True:
            await asyncio.sleep(1)
            await self.tick()

    async def tick(self):
        pass
