from fastapi import FastAPI
from central_server import create_app

app: FastAPI = create_app()
