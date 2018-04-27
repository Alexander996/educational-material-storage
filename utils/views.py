from datetime import datetime

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound
from sqlalchemy import select, column


class BaseView(web.View):
    model = None
    queryset = None
    serializer_class = None

    def get_model(self):
        assert self.model is not None, 'Set model in {}'.format(self.__class__.__name__)
        return self.model

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        assert self.serializer_class is not None, 'Set serializer_class in {}'.format(self.__class__.__name__)
        return self.serializer_class

    async def parse_records(self, records):
        res = {}
        async for row in records:
            for attr, value in row.items():
                if isinstance(value, datetime):
                    value = value.isoformat()
                res[attr] = value

        if not res:
            raise HTTPNotFound(text='{} not found'.format(self.model))

        return res


class DetailView(BaseView):
    async def get(self):
        pk = self.request.match_info['pk']
        model = self.get_model()
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()
        serializer = serializer()

        async with self.request.app['db'].acquire() as conn:
            where_params = model.c.id == pk
            if queryset is not None:
                where_params &= queryset

            columns = [column(field_name)
                       for field_name, field in serializer.serializer_fields.items()
                       if not field.write_only]

            query = select(columns).select_from(model).where(where_params)
            records = await conn.execute(query)
            res = await self.parse_records(records)
            return web.json_response(res)

    async def put(self):
        pk = self.request.match_info['pk']
        model = self.get_model()
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()

        request_data = await self.request.json()
        serializer = serializer(data=request_data)
        serializer.is_valid()

        async with self.request.app['db'].acquire() as conn:
            where_params = model.c.id == pk
            if queryset is not None:
                where_params &= queryset

            columns = [column(field_name)
                       for field_name, field in serializer.serializer_fields.items()
                       if not field.write_only]

            query = model.update().where(where_params).values(**serializer.validated_data)
            await conn.execute(query)

            query = select(columns).select_from(model).where(where_params)
            records = await conn.execute(query)
            res = await self.parse_records(records)
            return web.json_response(res)
