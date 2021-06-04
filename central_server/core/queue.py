from typing import NamedTuple, Callable
from enum import Enum
import heapq
from queue import PriorityQueue
from central_server.models import WindSpeed

class ServiceStatus(Enum):
    Waiting = 1
    Serving = 2

class Service(NamedTuple):
    room_id: str
    wind_speed: WindSpeed
    status: ServiceStatus
    time: int

    def __lt__(self, other):
        if self.status == ServiceStatus.Waiting:
            if self.wind_speed != other.wind_speed:
                return self.wind_speed > other.wind_speed
            return self.time < other.time
        else:
            if self.wind_speed != other.wind_speed:
                return self.wind_speed < other.wind_speed
            return self.time > other.time

class Queue:
    def __init__(self, expired_time, max_waiting_len):
        self.EXPIRED_TIME = expired_time
        self.MAX_WAITING_LEN = max_waiting_len

        self.queues = {
            ServiceStatus.Waiting: [],
            ServiceStatus.Serving: []
        }
        self.waiting_queue = []
        self.serving_queue = []


    def is_empty(self, status: ServiceStatus):
        return len(self.queues[status]) == 0

    def is_full_serving(self):
        return len(self.queues[ServiceStatus.Serving]) == self.MAX_WAITING_LEN

    def push(self, service: Service):
        if service.status == ServiceStatus.Serving and self.is_full_serving():
            return False
        heapq.heappush(self.queues[service.status], service)
        return True

    def pop_front(self, status: ServiceStatus):
        if self.is_empty(status):
            return None
        return heapq.heappop(self.queues[status])

    def front(self, status):
        if self.is_empty(status):
            return None
        return self.queues[status][0]

    def tick(self):
        for q in self.queues.items():
            for s in q:
                s.time += 1
