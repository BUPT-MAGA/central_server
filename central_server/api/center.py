from datetime import datetime, timedelta
from time import time
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from .body import *
from central_server.models import Admin, CheckIn, CheckInStatus, WindMode, Room, CenterStatus
from central_server.core import MyScheduler


def add_center_routes(app: FastAPI):
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/manager/login')

    @app.get('/')
    async def hello():
        return 'hello'

    @app.get("/items/")
    async def read_items(token: str = Depends(oauth2_scheme)):
        return {"token": token}

    @app.post('/manager/login')
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

    @app.post('/manager/register')
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

    @app.get('/air/list_checkin')
    async def list_checkin(token: str = Depends(oauth2_scheme)):
        return await CheckIn.list_all()

    @app.post('/air/checkin')
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

    @app.post('/air/checkout')
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
        await room.set.status(CheckInStatus.CheckOut)
        return check.dict()

    @app.get('/air/switch')
    async def switch_air(action: int = 1, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.status = CenterStatus(action)
        except:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The action is out of range",
            )
        return MyScheduler.status.value

    @app.get('/air/mode')
    async def set_mode(mode: int = 1, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.wind_mode = WindMode(mode)
        except:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The mode is out of range",
            )
        return MyScheduler.wind_mode.value

    @app.get('/air/temp')
    async def set_temp(temp: int = 0, token: str = Depends(oauth2_scheme)):
        try:
            MyScheduler.temperature = temp
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The temperature is not correspond to the current wind mode.",
            )
        return MyScheduler.temperature

    @app.get('/air/statistic')
    async def get_statistic(room_id: str = '', scale: int = 1, token: str = Depends(oauth2_scheme)):
        # TODO handle getting statistic
        if scale < 1 or scale > 3:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The scale is illegal",
            )

        return ''

    @app.get('/air/bill')
    async def get_bill(user_id: str, token: str = Depends(oauth2_scheme)):
        res: list = await CheckIn.get_bill(user_id=user_id)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no such user.",
            )
        return res

    @app.get('/air/room_info')
    async def get_room_info(token: str = Depends(oauth2_scheme)):
        res: list = await Room.get_info()
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no such user.",
            )
        return res

    @app.get('/air/room_status')
    async def get_room_status(room_id: str, token: str = Depends(oauth2_scheme)):
        res: Room = await Room.get(id=room_id)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="There's no such room.",
            )
        return res
