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
            return self.time > other.time
        else:
            if self.wind_speed != other.wind_speed:
                return self.wind_speed < other.wind_speed
            return self.time > other.time


class Queue:
    def __init__(self, expired_time, max_serving_len):
        self.EXPIRED_TIME = expired_time
        self.MAX_SERVING_LEN = max_serving_len

        self.queues = {
            ServiceStatus.Waiting: [],
            ServiceStatus.Serving: []
        }
        self.waiting_queue = []
        self.serving_queue = []

    def is_empty(self, status: ServiceStatus):
        return len(self.queues[status]) == 0

    def is_full_serving(self):
        return len(self.queues[ServiceStatus.Serving]) == self.MAX_SERVING_LEN

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

    def switch(self, service: Service):
        service.status = ServiceStatus.Waiting if service.status == ServiceStatus.Serving else ServiceStatus.Waiting
        service.time = 0

    def tick(self):
        for q in self.queues.items():
            for s in q:
                s.time += 1
        self.update()

    def update(self):
        # push waiting to serving
        if not self.is_full_serving():
            while not self.is_full_serving() and not self.is_empty(ServiceStatus.Waiting):
                waiting: Service = self.pop_front(ServiceStatus.Waiting)
                if waiting is not None:
                    self.switch(waiting)
                    self.push(waiting)
            return
        # exchange
        while not self.is_empty(ServiceStatus.Serving) and not self.is_empty(ServiceStatus.Waiting):
            last_serving: Service = self.front(ServiceStatus.Serving)
            first_waiting: Service = self.front(ServiceStatus.Waiting)
            if self.compare(last_serving, first_waiting):
                self.pop_front(ServiceStatus.Serving)
                self.pop_front(ServiceStatus.Waiting)
                self.switch(last_serving)
                self.switch(first_waiting)
                self.push(last_serving)
                self.push(first_waiting)
            else:
                break

    def compare(self, lhs: Service, rhs: Service):
        return lhs.wind_speed < rhs.wind_speed