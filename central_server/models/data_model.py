from typing import List
from tinydb import Query
from aiotinydb import AIOTinyDB

import config


def DataModel(pkey_field: str):
    def wrap(cls):
        data_name = cls.__name__
        db_path = config.DB_PATH
        item = Query()

        @staticmethod
        async def create(obj: cls) -> None:
            async with AIOTinyDB(db_path) as db:
                db.table(data_name).insert(obj.dict())

        @staticmethod
        async def where(q) -> List[cls]:
            async with AIOTinyDB(db_path) as db:
                res = db.table(data_name).search(q)
                return [cls(**x) for x in res]

        @staticmethod
        async def get(pkey):
            async with AIOTinyDB(db_path) as db:
                res = await cls.where(item[pkey_field] == pkey)
                return None if len(res) == 0 else res[0]

        @staticmethod
        async def update(field: str, value, q = None):
            async with AIOTinyDB(db_path) as db:
                db.table(data_name).update({field: value}) if q is None else db.table(data_name).update({field: value})


        def pkey(self: cls):
            return getattr(self, pkey_field)


        @staticmethod
        async def new(**kwargs):
            data = cls(**kwargs)
            if await cls.get(data.pkey()) is not None:
                raise RuntimeError(f'Can not create new {cls.__name__} with duplicated primary key {data.pkey()}')
            await cls._create(data)


        async def update_field(self: cls, field: str, value):
            pkey = self.dict()[pkey_field]
            setattr(self, field, value)
            await cls._update(field, value, item[pkey_field] == pkey)

        setattr(cls, 'item', item)
        # Never call `_create` directly, use `new` instead!
        setattr(cls, '_create', create)
        setattr(cls, 'new', new)
        setattr(cls, 'where', where)
        # Never call `_update` directly, get the data model object and use `update_field` instead!
        setattr(cls, '_update', update)
        setattr(cls, 'get', get)
        setattr(cls, 'pkey', pkey)
        setattr(cls, 'update_field', update_field)

        return cls

    return wrap
