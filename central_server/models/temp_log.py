from typing import NamedTuple, Optional, List
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel
from .room import WindSpeed
from .data_model import DataModel
from .my_types import EventType, Scale
from config import PRICE_TABLE
from central_server.utils import timestamp_to_tz, construct_weeks, construct_days, construct_months


@DataModel(pkey_field='id', auto_inc=True)
class TempLog(BaseModel):
    id: int
    room_id: str
    wind_speed: Optional[WindSpeed] = None
    timestamp: int
    event_type: EventType
    current_temp: Optional[int] = None
    current_fee: float = 0.0

    @staticmethod
    async def report_hotel(date: datetime, scale: Scale):
        ret = {}
        scaled_logs: List[TempLog] = await TempLog.filter(timestamp=lambda x: check_scale(x, date, scale))
        for log in scaled_logs:
            if log.room_id not in ret.keys():
                ret[log.room_id] = {'sum_fee': 0.0, 'open_cnt': 0, 'close_cnt': 0}
            if log.event_type == EventType.START:
                ret[log.room_id]['open_cnt'] += 1
            else:
                ret[log.room_id]['sum_fee'] += log.current_fee
                if log.event_type == EventType.END:
                    ret[log.room_id]['close_cnt'] += 1
        return ret

    @staticmethod
    async def report_room_span(room_id: str, date: datetime, scale: Scale, span: int):
        SPAN_HANDLER = {
            Scale.Day: construct_days,
            Scale.Week: construct_weeks,
            Scale.Month: construct_months,
        }
        dates = SPAN_HANDLER[scale](date, span)
        report = {}
        for d in dates:
            report[int(d.timestamp())] = await TempLog.report_room(room_id, d, scale)
        return report

    @staticmethod
    async def report_room(room_id: str, date: datetime, scale: Scale):
        DEFAULT_SPAN = {'start_time': 0, 'end_time': 0, 'start_temp': 0, 'end_temp': 0, 'fee': 0.0, 'wind': 0.0}
        ret = {'spans': [], 'sum_fee': 0.0, 'open_cnt': 0, 'close_cnt': 0}
        now_span = {}
        logs: List[TempLog] = await TempLog.get_all(room_id=room_id)
        scaled_logs: List[TempLog] = list(filter(lambda log: check_scale(log, date, scale), logs))
        for log in scaled_logs:
            if log.event_type == EventType.START:
                now_span = DEFAULT_SPAN
                now_span['start_time'] = log.timestamp
                now_span['start_temp'] = log.current_temp
                ret['open_cnt'] += 1
            else:
                now_span['fee'] += log.current_fee
                now_span['wind'] += PRICE_TABLE[log.wind_speed]
                ret['sum_fee'] += log.current_fee
                if log.event_type == EventType.END:
                    assert now_span['start_time'] != 0
                    now_span['end_time'] = log.timestamp
                    now_span['end_temp'] = log.current_temp
                    ret['close_cnt'] += 1
                    ret['spans'].append(now_span[log.room_id])
        return ret


def check_scale(log: TempLog, now_date: datetime, scale: Scale):
    log_date = timestamp_to_tz(log.timestamp)
    if scale == Scale.Day:
        return log_date.date() == now_date.date()
    elif scale == Scale.Week:
        return abs((now_date - log_date).days) < 7 and (log_date.weekday() < now_date.weekday()) == (
                    log_date < now_date)
    else:
        return log_date.year == now_date.year and log_date.month == now_date.month
