from json import JSONDecodeError

from aiohttp import web


class BaseView(web.View):
    _detail = None

    model = None
    queryset = None
    serializer_class = None

    @property
    def detail(self):
        assert self._detail is not None, 'Set _detail in {}'.format(self.__class__.__name__)
        return self._detail

    def get_model(self):
        assert self.model is not None, 'Set model in {}'.format(self.__class__.__name__)
        return self.model

    def get_queryset(self):
        queryset = None
        if self.detail:
            pk = self.model.c.id == self.request.match_info['pk']
            queryset = pk

        if self.queryset is not None:
            if queryset is not None:
                queryset &= self.queryset
            else:
                queryset = self.queryset
        return queryset

    def build_query(self, method, *args, **kwargs):
        func = getattr(self, '_build_' + method)
        query = func(*args, **kwargs)
        return query

    def _build_select(self, queryset):
        model = self.get_model()
        if queryset is not None:
            query = model.select().where(queryset)
        else:
            query = model.select()
        return query

    def _build_delete(self, queryset):
        model = self.get_model()
        query = model.delete().where(queryset)
        return query

    def _build_create(self, values):
        model = self.get_model()
        query = model.insert().values(**values)
        return query

    def _build_update(self, queryset, values):
        model = self.get_model()
        query = model.update().where(queryset).values(**values)
        return query

    def get_serializer(self):
        serializer = self.get_serializer_class()
        return serializer()

    def get_serializer_class(self):
        assert self.serializer_class is not None, 'Set serializer_class in {}'.format(self.__class__.__name__)
        return self.serializer_class

    async def get_json_data(self):
        try:
            data = await self.request.json()
        except JSONDecodeError:
            data = {}
        return data


class DetailView(BaseView):
    _detail = True

    async def get(self):
        async with self.request.app['db'].acquire() as conn:
            serializer = self.get_serializer()
            queryset = self.get_queryset()
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)

    async def delete(self):
        async with self.request.app['db'].acquire() as conn:
            queryset = self.get_queryset()
            query = self.build_query('delete', queryset=queryset)
            await conn.execute(query)
            return web.Response(status=204)

    async def put(self):
        response = await self._update(partial=False)
        return response

    async def patch(self):
        response = await self._update(partial=True)
        return response

    async def _update(self, partial=False):
        async with self.request.app['db'].acquire() as conn:
            serializer = self.get_serializer_class()
            queryset = self.get_queryset()
            request_data = await self.get_json_data()

            serializer = serializer(data=request_data)
            serializer.update_validate(partial=partial)

            if serializer.validated_data:
                query = self.build_query('update', values=serializer.validated_data, queryset=queryset)
                await conn.execute(query)

            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)


class ListView(BaseView):
    _detail = False

    async def get(self):
        async with self.request.app['db'].acquire() as conn:
            serializer = self.get_serializer_class()
            serializer = serializer(many=True)
            queryset = self.get_queryset()
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)

    async def post(self):
        async with self.request.app['db'].acquire() as conn:
            serializer = self.get_serializer_class()
            request_data = await self.get_json_data()

            serializer = serializer(data=request_data)
            serializer.create_validate()

            query = self.build_query('create', values=serializer.validated_data)
            insert = await conn.execute(query)

            model = self.get_model()
            queryset = model.c.id == insert.lastrowid

            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)
