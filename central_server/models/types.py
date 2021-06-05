from enum import IntEnum


class EventType(IntEnum):
    TEMP = 1
    START = 2
    END = 3


class CheckInStatus(IntEnum):
    CheckIn = 1
    CheckOut = 2


class AdminStatus(IntEnum):
    Off = 1
    On = 2


class WindMode(IntEnum):
    Snow = 1
    Sun = 2


class WindSpeed(IntEnum):
    Low = 1
    Mid = 2
    High = 3


    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
