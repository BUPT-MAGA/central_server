from .data_model import DataModel


class AdminData(DataModel):
    def __init__(self, db_path: str) -> 'AdminData':
        super().__init__(db_path, 'admin', 'username')
