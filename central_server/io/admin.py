from .data_model import DataModel
from central_server.models.admin import Admin


class AdminData(DataModel):
    def __init__(self, db_path: str) -> 'AdminData':
        super().__init__(db_path, 'admin', 'username', Admin)
