from aiohttp import web


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


class DetailView(BaseView):
    async def get(self):
        async with self.request.app['db'].acquire() as conn:
            pk = self.request.match_info['pk']
            model = self.get_model()
            queryset = self.get_queryset()
            serializer = self.get_serializer_class()
            serializer = serializer()

            where_params = model.c.id == pk
            if queryset is not None:
                where_params &= queryset

            query = model.select().where(where_params)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)

    async def put(self):
        async with self.request.app['db'].acquire() as conn:
            pk = self.request.match_info['pk']
            model = self.get_model()
            queryset = self.get_queryset()
            serializer = self.get_serializer_class()

            request_data = await self.request.json()
            serializer = serializer(data=request_data)
            serializer.is_valid()

            where_params = model.c.id == pk
            if queryset is not None:
                where_params &= queryset

            query = model.update().where(where_params).values(**serializer.validated_data)
            await conn.execute(query)

            query = model.select().where(where_params)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)
