from typing import Dict
from tinydb import TinyDB, Query
from central_server.utils import all_singletons


class DBInstance(object):
    def __init__(self):
        self.db_dict: Dict[str, TinyDB] = dict()

    def get_db(self, db_path: str):
        if db_path not in self.db_dict:
            self.db_dict[db_path] = TinyDB(db_path)
        return self.db_dict[db_path]


all_singletons.register(DBInstance)
