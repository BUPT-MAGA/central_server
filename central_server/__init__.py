from flask import Flask

from central_server.api.center import add_center_routes

def create_app():
    app = Flask(__name__)

    add_center_routes(app)

    return app
