from typing import NamedTuple, Callable
from tinydb import TinyDB, Query

from .db_instance import DBInstance


class DataModel(object):
    def init_db(db_path: str):
        db_inst = DBInstance()
        return db_inst.get_db(db_path)

    Data = Query()

    def __init__(self,
                 db_path: str,
                 data_name: str, primary_key: str, constructor: type):
        self.db = self.init_db(db_path)
        self.data_name = data_name
        self.table = self.db.table(self.data_name)
        self.primary_key = primary_key
        self.constructor = constructor

    def insert(self, data: NamedTuple):
        self.table.insert(data.dict())

    def get(self, pid):
        res = self.table.search(Data[self.primary_key] == pid)
        if len(res) == 0:
            return None
        else:
            res = res[0]
            return self.constructor(**res)

    def update(self, pid, field_name: str, value):
        self.table.update({field_name: value}, Data[self.primary_key] == pid)
