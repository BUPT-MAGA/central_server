from datetime import datetime, timedelta
from config import TIME_ZONE


def timestamp_to_tz(timestamp: int):
    return datetime.fromtimestamp(float(timestamp), tz=TIME_ZONE)


def construct_months(date: datetime, span: int):
    ret = [date]
    for i in range(span - 1):
        first_day = ret[-1].replace(day=1)
        last_month = first_day - timedelta(days=1)
        ret.append(last_month)
    return list(reversed(ret))


def construct_weeks(date: datetime, span: int):
    ret = [date]
    for i in range(span - 1):
        ret.append(ret[-1] - timedelta(weeks=1))
    return list(reversed(ret))


def construct_days(date: datetime, span: int):
    ret = [date]
    for i in range(span - 1):
        ret.append(ret[-1] - timedelta(days=1))
    return list(reversed(ret))
