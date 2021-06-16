import os
import sys
import traceback
from datetime import datetime, timedelta
from time import time
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from central_server.api.conn_manager import MyManager
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, decode_access_token
from .body import *
from central_server.models import Admin, CheckIn, CheckInStatus, WindMode, Room, CenterStatus, TempLog, Scale, WindSpeed
from central_server.core import MyScheduler
from central_server.utils import timestamp_to_tz
from central_server.reporting import center_api
from config import REPORT_SPAN, UNIT_PRICE, MAX_SERVING_LEN


# TODO fix size rooms

def add_center_routes(app: FastAPI):
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/manager/login')

    @app.get('/')
    async def hello():
        return 'hello'

    @app.get("/items/")
    async def read_items(token: str = Depends(oauth2_scheme)):
        return {"token": token}

    @app.post('/api/manager/login')
    async def login(form: OAuth2PasswordRequestForm = Depends()):
        username = form.username
        password = form.password
        user = await Admin.check(username=username, password=password)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @app.post('/api/manager/register')
    async def register(admin_req: AdminReq):
        username = admin_req.username
        password = admin_req.password
        check = await Admin.check(username, password)
        if check is not None:
            print(check)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate username",
            )
        user: Admin = await Admin.new(username=username, password=password)
        return user.dict()

    @app.get('/api/profile')
    async def get_profile(token: str = Depends(oauth2_scheme)):
        if token is None:
            return {}
        user: dict = decode_access_token(token)
        return {'username': user['sub'], 'role': 'admin'}

    @app.get('/api/list_checkin')
    async def list_checkin(token: str = Depends(oauth2_scheme)):
        return await CheckIn.list_all()

    @app.get('/api/settings/init')
    async def init(token: str = Depends(oauth2_scheme)):
        return {
            'switch': True if MyScheduler.status == CenterStatus.On else False,
            'mode': MyScheduler.wind_mode,
            'temp': MyScheduler.temperature,
            'fee': UNIT_PRICE,
            'slave': MAX_SERVING_LEN
        }

    async def db_create_room(room_id: str):
        data = {
            'id': room_id,
            'status': CheckInStatus.CheckIn,
            'wind_mode': WindMode.Snow,
            'wind_speed': WindSpeed.Low,
            'current_temp': 30,
            'target_temp': 25,
        }
        res = await Room.new(**data)
        center_api.info(f'room created: {res}')
        return res

    @app.post('/api/checkin')
    async def check_in(checkin_req: CheckReq, token: str = Depends(oauth2_scheme)):
        room_id = checkin_req.room_id
        user_id = checkin_req.user_id
        check = await CheckIn.check(room_id=room_id, status=CheckInStatus.CheckIn)
        if check is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The room has checked in",
            )
        check_in_log: CheckIn = await CheckIn.new(user_id=user_id,
                                                  room_id=room_id,
                                                  checkin_time=int(time()))
        # TODO: new a room when a slave connection comes
        room = await Room.get(room_id)
        room = await db_create_room(room_id) if room is None else room
        await room.set.status(CheckInStatus.CheckIn)
        return check_in_log.dict()

    @app.post('/api/checkout')
    async def check_out(checkout_req: CheckReq, token: str = Depends(oauth2_scheme)):
        room_id = checkout_req.room_id
        user_id = checkout_req.user_id
        check: CheckIn = await CheckIn.check(room_id=room_id, user_id=user_id, status=CheckInStatus.CheckIn)
        if check is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The user has not checked in",
            )
        await check.set.checkout_time(int(time()))
        await check.set.status(CheckInStatus.CheckOut)
        room = await Room.get(check.room_id)
        if room is not None:
            await room.set.status(CheckInStatus.CheckOut)
        return check.dict()

    @app.get('/api/settings/switch')
    async def switch_air(action: int = 1, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.status = CenterStatus(action)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The action is out of range",
            )
        return MyScheduler.status.value

    @app.get('/api/settings/mode')
    async def set_mode(mode: int = 1, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.wind_mode = WindMode(mode)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The mode is out of range",
            )
        return MyScheduler.wind_mode.value

    @app.get('/api/settings/temp')
    async def set_temp(temp: int = 0, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.temperature = temp
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The temperature is not correspond to the current wind mode.",
            )
        return MyScheduler.temperature

    @app.get('/api/settings/slave')
    async def set_temp(slave: int = MAX_SERVING_LEN, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.max_serving_len = slave
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The slave is not valid.",
            )
        return MyScheduler.max_serving_len

    @app.get('/api/settings/fee')
    async def set_temp(fee: float = UNIT_PRICE, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.unit_price = fee
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The unit price is not valid.",
            )
        return MyScheduler.unit_price

    @app.get('/api/report_hotel')
    async def report_hotel(timestamp: int, scale: int = 1, token: str = Depends(oauth2_scheme)):
        try:
            print(scale)
            res = await TempLog.report_hotel(timestamp_to_tz(timestamp), Scale(scale))
            print(res)

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The scale is illegal",
            )
        return res

    @app.get('/api/report_room')
    async def report_room(room_id: str, timestamp: int, scale: int = 1, span: int = REPORT_SPAN,
                          token: str = Depends(oauth2_scheme)):
        try:
            # is_room = await Room.exists(id=room_id)
            # if not is_room:
            #     print(is_room)
            #     raise HTTPException(
            #         status_code=status.HTTP_409_CONFLICT,
            #         detail="The room doesn't exist",
            #     )
            res = await TempLog.report_room_span(room_id, timestamp_to_tz(timestamp), Scale(scale), span)
            # if len(res) == 0:
            # res = {
            #     1615651200: {
            #         'spans': [
            #             {'start_time': 12312312, 'end_time': 12312512, 'start_temp': 20, 'end_temp': 25, 'fee': 4.0,
            #              'wind': 3.0},
            #             {'start_time': 12312612, 'end_time': 12312712, 'start_temp': 22, 'end_temp': 25, 'fee': 3.0,
            #              'wind': 3.0}], 'sum_fee': 3.0, 'open_cnt': 3, 'close_cnt': 3
            #     },
            #     1618329600: {
            #         'spans': [
            #             {'start_time': 12312312, 'end_time': 12312512, 'start_temp': 20, 'end_temp': 25, 'fee': 4.0,
            #              'wind': 3.0},
            #             {'start_time': 12312612, 'end_time': 12312712, 'start_temp': 22, 'end_temp': 25, 'fee': 3.0,
            #              'wind': 3.0}], 'sum_fee': 4.0, 'open_cnt': 3, 'close_cnt': 3
            #     },
            #     1620921600: {
            #         'spans': [
            #             {'start_time': 12312312, 'end_time': 12312512, 'start_temp': 20, 'end_temp': 25, 'fee': 4.0,
            #              'wind': 3.0},
            #             {'start_time': 12312612, 'end_time': 12312712, 'start_temp': 22, 'end_temp': 25, 'fee': 3.0,
            #              'wind': 3.0}], 'sum_fee': 19.0, 'open_cnt': 3, 'close_cnt': 3
            #     },
            #     1623600000: {
            #         'spans': [
            #             {'start_time': 12312312, 'end_time': 12312512, 'start_temp': 20, 'end_temp': 25, 'fee': 4.0,
            #              'wind': 3.0},
            #             {'start_time': 12312612, 'end_time': 12312712, 'start_temp': 22, 'end_temp': 25, 'fee': 3.0,
            #              'wind': 3.0}], 'sum_fee': 2.0, 'open_cnt': 3, 'close_cnt': 3
            #     },
            #     1626192000: {
            #         'spans': [
            #             {'start_time': 12312312, 'end_time': 12312512, 'start_temp': 20, 'end_temp': 25, 'fee': 4.0,
            #              'wind': 3.0},
            #             {'start_time': 12312612, 'end_time': 12312712, 'start_temp': 22, 'end_temp': 25, 'fee': 3.0,
            #              'wind': 3.0}], 'sum_fee': 10.0, 'open_cnt': 3, 'close_cnt': 3
            #     },
            #     1628870400: {
            #         'spans': [
            #             {'start_time': 12312312, 'end_time': 12312512, 'start_temp': 20, 'end_temp': 25, 'fee': 4.0,
            #              'wind': 3.0},
            #             {'start_time': 12312612, 'end_time': 12312712, 'start_temp': 22, 'end_temp': 25, 'fee': 3.0,
            #              'wind': 3.0}], 'sum_fee': 3.0, 'open_cnt': 3, 'close_cnt': 3
            #     }
            # }
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The scale is illegal",
            )
        return res

    @app.get('/api/bill')
    async def get_bill(user_id: str, token: str = Depends(oauth2_scheme)):
        res: list = await CheckIn.get_bill(user_id=user_id)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no such user.",
            )
        # FIXME: mock
        # if len(res) == 0:
        #     res = []
        #     bill = {}
        #     bill['room_id'] = '120'
        #     bill['status'] = 1
        #     bill['checkin_time'] = 112313
        #     bill['fee'] = 1.0
        #     res.append(bill)
        return res

    @app.get('/api/room_info')
    async def get_room_info(token: str = Depends(oauth2_scheme)):
        res: list = await Room.get_info()
        # FIXME
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no rooms.",
            )
        # FIXME: mock
        # if len(res) == 0:
        #     res = []
        #     info = {}
        #     info['room_id'] = '2'
        #     info['status'] = 1
        #     info['user_id'] = '2'
        #     res.append(info)
        return res

    @app.get('/api/room_status')
    async def get_room_status(token: str = Depends(oauth2_scheme)):
        res: List = await Room.get_status()
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no such room whose ac is open.",
            )

        next_res = []
        for x in res:
            x = x.dict()
            room_id = x['id']

            # pack serving status
            is_serving = await MyScheduler.is_serving(room_id)
            if not is_serving:
                x['wind_speed'] = -1

            # pack connecetion status
            check_in1: CheckIn = await CheckIn.get_last(room_id=room_id)
            if check_in1 is None:
                x['is_online'] = False
            else:
                check_in_id = check_in1.id
                x['is_online'] = check_in_id in MyManager.active_connections

            next_res.append(x)

        # if len(res) == 0:
        #     FIXME: mock
            # res = [{1623819629
            #     'room_id': '120',
            #     'status': 1,
            #     'wind_mode': 1,
            #     'wind_speed': 1,
            #     'current_temp': 20,
            #     'target_temp': 25
            # }, {
            #     'room_id': '120',
            #     'status': 1,
            #     'wind_mode': 1,
            #     'wind_speed': 1,
            #     'current_temp': 20,
            #     'target_temp': 25
            # }]
        return next_res
