from typing import Dict
from tinydb import TinyDB, Query


class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance


class DBInstance(Singleton):
    def __init__(self):
        self.db_dict: Dict[str, TinyDB] = dict()

    def get_db(db_path: str):
        if db_path not in self.db_dict:
            self.db_dict[db_path] = TinyDB(db_path)
        return self.db_dict[db_path]

