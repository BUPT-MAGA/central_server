from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from .body import *
from central_server.models import Admin, CheckIn, CheckInStatus

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
        # FIXME: get current time from Scheduler
        check_in_log: CheckIn = await CheckIn.new(user_id=user_id, room_id=room_id, checkin_time=0)
        return check_in_log.dict()

    @app.post('/air/checkout')
    async def check_out(checkout_req: CheckReq, token: str = Depends(oauth2_scheme)):
        room_id = checkout_req.room_id
        user_id = checkout_req.user_id
        check = await CheckIn.check(room_id=room_id, user_id=user_id, status=CheckInStatus.CheckIn)
        if check is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The user has not checked in",
            )
        # FIXME: get current time from Scheduler
        await check.set.checkout_time(0)
        await check.set.status(CheckInStatus.CheckOut)
        return check.dict()

    @app.get('/air/switch')
    async def switch_air(action: int = 0, token: str = Depends(oauth2_scheme)):
        # TODO handle switch
        return 'switch successfully'

    @app.get('/air/mode')
    async def set_mode(mode: int = 0, token: str = Depends(oauth2_scheme)):
        # TODO handle setting mode
        return 'set mode successfully'

    @app.get('/air/statistic')
    async def get_statistic(room_id: str = '', scale: int = 0, token: str = Depends(oauth2_scheme)):
        # TODO handle getting statistic
        return ''
