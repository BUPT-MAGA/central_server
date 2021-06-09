from datetime import datetime, timedelta
from time import time
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, decode_access_token
from .body import *
from central_server.models import Admin, CheckIn, CheckInStatus, WindMode, Room, CenterStatus, TempLog, Scale
from central_server.core import MyScheduler
from central_server.utils import timestamp_to_tz
from config import REPORT_SPAN

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
        room = await Room.get_first(room_id=check.room_id)
        if room is not None:
            await room.set.status(CheckInStatus.CheckOut)
        return check.dict()

    @app.get('/api/switch')
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

    @app.get('/api/mode')
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

    @app.get('/api/temp')
    async def set_temp(temp: int = 0, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.temperature = temp
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The temperature is not correspond to the current wind mode.",
            )
        return MyScheduler.temperature

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
    async def report_room(room_id: str, timestamp: int ,scale: int = 1, span: int = REPORT_SPAN, token: str = Depends(oauth2_scheme)):
        try:
            print(scale)
            res = await TempLog.report_room_span(room_id, timestamp_to_tz(timestamp), Scale(scale), span)
            print(res)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The scale is illegal",
            )
        # res = {
        #     '120': {
        #         'spans': [{'start_time': 0, 'end_time': 0, 'start_temp': 0, 'end_temp': 0, 'fee': 0.0, 'wind': 0.0}],
        #         'open_cnt': 0,
        #         'close_cnt': 0,
        #         'sum_fee': 0.0
        #     }
        # }
        return res

    @app.get('/api/bill')
    async def get_bill(user_id: str, token: str = Depends(oauth2_scheme)):
        res: list = await CheckIn.get_bill(user_id=user_id)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no such user.",
            )
        return res

    @app.get('/api/room_info')
    async def get_room_info(token: str = Depends(oauth2_scheme)):
        res: list = await Room.get_info()
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no rooms.",
            )
        return res

    @app.get('/api/room_status')
    async def get_room_status(token: str = Depends(oauth2_scheme)):
        res: List[Room] = await Room.get_status()
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no such room whose ac is open.",
            )
        # res = [{
        #     'room_id': '120',
        #     'status': 1,
        #     'wind_mode': 1,
        #     'wind_speed': 1,
        #     'current_temp': 20,
        #     'target_temp': 25,
        #     'served_time': 2,
        #     'wait_time': 3
        # },{
        #     'room_id': '120',
        #     'status': 1,
        #     'wind_mode': 1,
        #     'wind_speed': 1,
        #     'current_temp': 20,
        #     'target_temp': 25,
        #     'served_time': 2,
        #     'wait_time': 3
        # }]
        return res
