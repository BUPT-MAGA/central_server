from flask import Blueprint, Flask, request
from flask_login import login_user
import json

def add_center_routes(app: Flask):
    @app.route('/manager/login', methods=['POST'])
    def login():
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            # TODO
            # https://github.com/PrettyPrinted/flask_auth_scotch/blob/master/project/auth.py
            # login_user()

    @app.route('/manager/register', methods=['POST'])
    def register():
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            # TODO
            # https://github.com/PrettyPrinted/flask_auth_scotch/blob/master/project/auth.py
            # login_user()

    @app.route('/air/switch', methods=['GET'])
    def switch_air():
        action = int(request.args.get('action', 0))
        # TODO handle switch
        return 'switch successfully'

    @app.route('/air/mode', methods=['GET'])
    def set_mode():
        mode = int(request.args.get('mode', 0))
        # TODO handle setting mode
        return 'set mode successfully'

    @app.route('/air/statistic', methods=['GET'])
    def get_statistic():
        roomId = request.args.get('roomId', '')
        scale = request.args.get('scale', 0)
        # TODO handle getting statistic
        return json.dumps(dict())
