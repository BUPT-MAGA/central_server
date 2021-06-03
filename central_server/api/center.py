from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from .body import *
from central_server.models.admin import Admin

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
        user = Admin.auth(username, password)
        if not user:
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
        check = Admin.check(username)
        if not check:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate username",
            )
        user: Admin = Admin.register(username, password)
        return user._as_dict()

    @app.post('/air/checkin')
    async def check_in(checkin_req: CheckInReq):
        room_id = checkin_req.room_id
        user_id = checkin_req.user_id
        # TODO

    @app.get('/air/switch')
    async def switch_air(action: int = 0, token: str = Depends(oauth2_scheme)):
        # TODO handle switch
        return 'switch successfully'

    @app.get('/air/mode')
    async def set_mode(mode: int = 0, token: str = Depends(oauth2_scheme)):
        # TODO handle setting mode
        return 'set mode successfully'

    @app.get('/air/statistic')
    async def get_statistic(roomId: str = '', scale: int = 0, token: str = Depends(oauth2_scheme)):
        # TODO handle getting statistic
        return json.dumps(dict())
