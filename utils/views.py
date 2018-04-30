from aiohttp import web


class BaseView(web.View):
    _detail = False

    model = None
    queryset = None
    serializer_class = None

    @property
    def detail(self):
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
        query = func(self.get_queryset(), *args, **kwargs)
        return query

    def _build_select(self, queryset):
        model = self.get_model()
        if queryset is not None:
            query = model.select().where(queryset)
        else:
            query = model.select()
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


class DetailView(BaseView):
    _detail = True

    async def get(self):
        async with self.request.app['db'].acquire() as conn:
            serializer = self.get_serializer()
            query = self.build_query('select')
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)

    async def put(self):
        async with self.request.app['db'].acquire() as conn:
            serializer = self.get_serializer_class()
            request_data = await self.request.json()
            serializer = serializer(data=request_data)
            serializer.is_valid()

            query = self.build_query('update', values=serializer.validated_data)
            await conn.execute(query)

            query = self.build_query('select')
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)
