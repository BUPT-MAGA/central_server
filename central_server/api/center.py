from fastapi import FastAPI
import json

def add_center_routes(app: FastAPI):
    @app.get('/')
    async def hello():
        return 'hello'

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
