import os
from central_server.models import WindMode

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

REAL_SEC_PER_MIN = 1
REQ_EXPIRED_TIME = 30
TOKEN_EXPIRED_TIME = 100

MAX_SERVING_LEN = 3

TEMP_RANGE = {
    WindMode.Snow: range(18, 26),
    WindMode.Sun: range(25, 31)
}

TEMP_DEFAULT = {
    WindMode.Snow: 22,
    WindMode.Sun: 28
}
