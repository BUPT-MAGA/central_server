from flask import Blueprint, Flask

def add_center_routes(app: Flask):
    @app.route('/')
    def hello():
        return 'hello world'