from .data_model import DataModel
from central_server.models.check_in import CheckIn


class CheckInData(DataModel):
    def __init__(self, db_path: str) -> 'CheckInData':
        super().__init__(db_path, 'check_in', 'id', CheckIn)
