from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from config import DB_PATH

_db = None


def get_db() -> TinyDB:
    global _db
    if _db is None:
        _db = TinyDB(DB_PATH, storage=CachingMiddleware(JSONStorage))
    return _db

