from enum import IntEnum


class EventType(IntEnum):
    TEMP = 1
    START = 2
    END = 3
    # 从机上线
    ONLINE = 4
    # 从机下线
    OFFLINE = 5


class CheckInStatus(IntEnum):
    CheckIn = 1
    CheckOut = 2


class AdminStatus(IntEnum):
    Off = 1
    On = 2


class CenterStatus(IntEnum):
    Off = 1
    On = 2


class WindMode(IntEnum):
    Snow = 0
    Sun = 1


class WindSpeed(IntEnum):
    Low = 0
    Mid = 1
    High = 2

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Scale(IntEnum):
    Day = 1
    Week = 2
    Month = 3
