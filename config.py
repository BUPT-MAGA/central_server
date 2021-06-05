import os
from central_server.models.types import WindMode, WindSpeed

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DB_PATH = 'db.json'

REAL_SEC_PER_MIN = 1        # eg. 1 sec in the real world means 1 min in maga.
REQ_EXPIRED_TIME = 30       # drop too long service in queue
TOKEN_EXPIRED_TIME = 100    # minutes

MAX_SERVING_LEN = 3         # capacity of serving queue

# temperature range for different modes
TEMP_RANGE = {
    WindMode.Snow: range(18, 26),
    WindMode.Sun: range(25, 31)
}

TEMP_DEFAULT = {
    WindMode.Snow: 22,
    WindMode.Sun: 28
}

PRICE_TABLE = {
    WindSpeed.Low: 0.8,
    WindSpeed.Mid: 1.0,
    WindSpeed.High: 1.2
}

UNIT_PRICE = 5.0
