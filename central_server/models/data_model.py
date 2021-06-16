from typing import List
from tinydb import Query, TinyDB
from central_server.models.db import get_db

import config


def DataModel(pkey_field: str, auto_inc: bool = False):
    def build_query(**kwargs):
        items = list(kwargs.items())
        q = Query()[items[0][0]] == items[0][1]
        for item in items[1:]:
            q = q & (Query()[item[0]] == item[1])
        return q

    def build_filter(**kwargs):
        items = list(kwargs.items())
        q = Query()[items[0][0]].test(items[0][1])
        for item in items[1:]:
            q = q & (Query()[item[0]].test(item[1]))
        return q

    def wrap(cls):
        data_name = cls.__name__
        db_path = config.DB_PATH
        item = Query()

        @staticmethod
        async def create(obj: cls) -> None:
            db = get_db()
            db.table(data_name).insert(obj.dict())
            return obj

        @staticmethod
        async def where(q) -> List[cls]:
            db = get_db()
            res = db.table(data_name).search(q)
            return [cls(**x) for x in res]

        @staticmethod
        async def get(pkey):
            db = get_db()
            res = await cls.where(item[pkey_field] == pkey)
            return None if len(res) == 0 else res[0]

        @staticmethod
        async def filter(**kwargs):
            return await cls.where(build_filter(**kwargs))

        @staticmethod
        async def get_all(**kwargs):
            return await cls.where(build_query(**kwargs))

        @staticmethod
        async def list_all():
            db = get_db()
            res = db.table(data_name).all()
            return [cls(**x) for x in res]

        @staticmethod
        async def get_first(**kwargs):
            res = await cls.get_all(**kwargs)
            if len(res) == 0:
                return None
            else:
                return res[0]

        @staticmethod
        async def get_last(**kwargs):
            res = await cls.get_all(**kwargs)
            if len(res) == 0:
                return None
            else:
                return res[-1]

        @staticmethod
        async def update(field: str, value, q=None):
            db = get_db()
            db.table(data_name).update({field: value}) if q is None \
                else db.table(data_name).update({field: value}, q)

        @staticmethod
        async def exists(**kwargs):
            res = await cls.where(build_query(**kwargs))
            return len(res) > 0

        async def inc_pkey():
            db = get_db()
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
            return await cls._create(data)

        async def update_field(self: cls, field: str, value):
            pkey = self.dict()[pkey_field]
            setattr(self, field, value)
            await cls._update(field, value, item[pkey_field] == pkey)

        class FieldUpdater(object):
            def __init__(self, data_self):
                self.data_self = data_self

            def __getattr__(self, item):
                async def func(value):
                    await self.data_self.update_field(item, value)

                return func

        @property
        def field_updater(self):
            return FieldUpdater(self)

        setattr(cls, 'item', item)
        # Never call `_create` directly, use `new` instead!
        setattr(cls, '_create', create)
        setattr(cls, 'new', new)
        setattr(cls, 'where', where)
        setattr(cls, 'filter', filter)
        setattr(cls, 'get_all', get_all)
        setattr(cls, 'get_first', get_first)
        setattr(cls, 'get_last', get_last)
        setattr(cls, 'list_all', list_all)
        setattr(cls, 'exists', exists)
        # Never call `_update` directly, get the data model object and use `update_field` instead!
        setattr(cls, '_update', update)
        setattr(cls, 'get', get)
        setattr(cls, 'pkey', pkey)
        setattr(cls, 'update_field', update_field)
        # `set` is syntax sugar: obj.update_field('field', value) is equivalent to obj.set.field(value)
        setattr(cls, 'set', field_updater)

        return cls

    return wrap
