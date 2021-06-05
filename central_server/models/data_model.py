from typing import List
from tinydb import Query
from aiotinydb import AIOTinyDB

import config


def DataModel(pkey_field: str, auto_inc: bool = False):
    def build_query(**kwargs):
        items = list(kwargs.items())
        q = Query()[items[0][0]] == items[0][1]
        for item in items[1:]:
            q = q & (Query()[item[0]] == item[1])
        return q

    def wrap(cls):
        data_name = cls.__name__
        db_path = config.DB_PATH
        item = Query()

        @staticmethod
        async def create(obj: cls) -> None:
            async with AIOTinyDB(db_path) as db:
                db.table(data_name).insert(obj.dict())
                return obj

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
        async def get_all(**kwargs):
            return await cls.where(build_query(**kwargs))


        @staticmethod
        async def get_first(**kwargs):
            res = await cls.get_all(**kwargs)
            if len(res) == 0:
                return None
            else:
                return res[0]

        @staticmethod
        async def update(field: str, value, q = None):
            async with AIOTinyDB(db_path) as db:
                db.table(data_name).update({field: value}) if q is None else db.table(data_name).update({field: value})


        @staticmethod
        async def exists(q):
            async with AIOTinyDB(db_path) as db:
                res = db.table(data_name).search(q)
                return len(res) > 0


        async def inc_pkey():
            async with AIOTinyDB(db_path) as db:
                table = db.table('_primary_key')
                q = Query().data_name == data_name
                res = table.search(q)
                if len(res) == 0:
                    table.insert({'data_name': data_name, 'value': 1})
                    return 0
                else:
                    pkey = res[0]['value']
                    table.update({'value': pkey + 1}, q)
                    return pkey



        def pkey(self: cls):
            return getattr(self, pkey_field)


        @staticmethod
        async def new(**kwargs):
            if auto_inc:
                pkey = await inc_pkey()
                kwargs[pkey_field] = pkey
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
        setattr(cls, 'get_all', get_all)
        setattr(cls, 'get_first', get_first)
        setattr(cls, 'exists', exists)
        # Never call `_update` directly, get the data model object and use `update_field` instead!
        setattr(cls, '_update', update)
        setattr(cls, 'get', get)
        setattr(cls, 'pkey', pkey)
        setattr(cls, 'update_field', update_field)

        return cls

    return wrap
