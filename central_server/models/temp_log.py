from typing import NamedTuple, Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from .room import WindSpeed
from .data_model import DataModel
from .my_types import EventType, Scale
from config import PRICE_TABLE


@DataModel(pkey_field='id', auto_inc=True)
class TempLog(BaseModel):
    id: int
    room_id: str
    wind_speed: Optional[WindSpeed]
    timestamp: str
    event_type: EventType
    current_temp: int
    current_fee: float = 0.0

    @staticmethod
    async def get_statistic(scale: Scale):
        DEFAULT_SPAN = {'start_time': 0, 'end_time': 0, 'start_temp': 0, 'end_temp': 0, 'fee': 0.0, 'wind': 0.0}
        ret = {}
        now_span = {}
        logs: List[TempLog] = TempLog.list_all()
        scaled_logs: List[TempLog] = list(filter(lambda log: check_scale(log, scale), logs))
        for log in scaled_logs:
            if log.room_id not in ret.keys():
                ret[log.room_id] = {'sum_fee': 0.0, 'spans': []}
                ret[log.room_id].setdefault('open_cnt', 0)
                ret[log.room_id].setdefault('close_cnt', 0)
            if log.event_type == EventType.START:
                now_span[log.room_id] = DEFAULT_SPAN
                now_span[log.room_id]['start_time'] = log.timestamp
                now_span[log.room_id]['start_temp'] = log.current_temp
                ret[log.room_id]['open_cnt'] += 1
            else:
                now_span[log.room_id]['fee'] += log.current_fee
                now_span[log.room_id]['wind'] += PRICE_TABLE[log.wind_speed]
                ret[log.room_id]['sum_fee'] += log.current_fee
                if log.event_type == EventType.END:
                    assert now_span[log.room_id]['start_time'] != 0
                    now_span[log.room_id]['end_time'] = log.timestamp
                    now_span[log.room_id]['end_temp'] = log.current_temp
                    ret[log.room_id]['close_cnt'] += 1
                    ret[log.room_id]['spans'].append(now_span[log.room_id])
        return ret


def check_scale(log: TempLog, scale: Scale):
    log_date = datetime.fromtimestamp(float(log.timestamp))
    now_date = datetime.today()
    if scale == Scale.Day:
        return log_date.date() == now_date.date()
    elif scale == Scale.Week:
        return (now_date - log_date).days < 7 and log_date.weekday() < now_date.weekday()
    else:
        return log_date.year == now_date.year and log_date.month == now_date.month
