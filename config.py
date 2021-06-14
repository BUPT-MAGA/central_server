import os
import pytz
from central_server.models.my_types import WindMode, WindSpeed, Scale

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DB_PATH = 'database.json'

WORK_RATE = 1  # eg. work every 1 sec
REQ_EXPIRED_TIME = 30  # drop too long service in queue
TOKEN_EXPIRED_TIME = 100  # minutes

MAX_SERVING_LEN = 3  # capacity of serving queue

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

REPORT_SPAN = 6
TIME_ZONE = pytz.timezone('Asia/Shanghai')
