from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
from .security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
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



    # @app.post('/manager/login', methods=['POST'])
    # def login():
    #     if 'username' in request.form and 'password' in request.form:
    #         username = request.form['username']
    #         password = request.form['password']
    #         TODO
    #         https://github.com/PrettyPrinted/flask_auth_scotch/blob/master/project/auth.py
    #         login_user()
    #
    # @app.route('/manager/register', methods=['POST'])
    # def register():
    #     if 'username' in request.form and 'password' in request.form:
    #         username = request.form['username']
    #         password = request.form['password']
    #         TODO
    #         https://github.com/PrettyPrinted/flask_auth_scotch/blob/master/project/auth.py
            # login_user()

    @app.get('/air/switch')
    async def switch_air(action: int = 0):
        # TODO handle switch
        return 'switch successfully'

    @app.get('/air/mode')
    async def set_mode(mode: int = 0):
        # TODO handle setting mode
        return 'set mode successfully'

    @app.get('/air/statistic')
    async def get_statistic(roomId: str = '', scale: int = 0):
        # TODO handle getting statistic
        return json.dumps(dict())
