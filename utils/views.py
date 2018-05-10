import tempfile
from datetime import datetime

from aiohttp import web, hdrs
from aiohttp.web_request import FileField
from aiohttp_cors import CorsViewMixin

from project import settings
from project.settings import MEDIA_ROOT, MEDIA_URL, CHUNK_SIZE
from utils.exceptions import ValidationError
from utils.media import generate_path_to_file, generate_file_name


class BaseView(web.View, CorsViewMixin):
    _detail = None

    model = None
    queryset = None
    serializer_class = None
    pagination_class = settings.DEFAULT_PAGINATION_CLASS
    page_limit = settings.PAGE_LIMIT

    @property
    def detail(self):
        assert self._detail is not None, 'Set _detail in {}'.format(self.__class__.__name__)
        return self._detail

    def get_model(self):
        assert self.model is not None, 'Set model in {}'.format(self.__class__.__name__)
        return self.model

    def get_pagination_class(self):
        return self.pagination_class(self.page_limit, self.request) if self.pagination_class is not None else None

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

    def get_serializer(self, *args, **kwargs):
        serializer = self.get_serializer_class()
        return serializer(*args, context={'request': self.request}, **kwargs)

    def get_serializer_class(self):
        assert self.serializer_class is not None, 'Set serializer_class in {}'.format(self.__class__.__name__)
        return self.serializer_class


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
            queryset = self.get_queryset()
            request_data = await get_json_data(self.request)

            serializer = self.get_serializer(data=request_data)
            await serializer.update_validate(partial=partial)

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
            serializer = self.get_serializer(many=True)
            queryset = self.get_queryset()
            query = self.build_query('select', queryset=queryset)

            paginator = self.get_pagination_class()
            if paginator is not None:
                query = paginator.paginate_query(query)

            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data)

    async def post(self):
        if self.request.content_type == 'multipart/form-data':
            return await self.multipart_post()

        async with self.request.app['db'].acquire() as conn:
            model = self.get_model()
            request_data = await get_json_data(self.request)
            serializer = self.get_serializer(data=request_data)
            await serializer.create_validate()

            query = self.build_query('create', values=serializer.validated_data)
            insert = await conn.execute(query)

            queryset = model.c.id == insert.lastrowid
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data, status=201)

    async def multipart_post(self):
        async with self.request.app['db'].acquire() as conn:
            now = datetime.now()
            model = self.get_model()
            if self.request.can_read_body:
                data = await get_multipart_data(self.request)
            else:
                data = {}

            serializer = self.get_serializer(data=data)
            await serializer.create_validate()

            files = serializer.file_fields
            for file_name, file in files.items():
                path = generate_path_to_file(MEDIA_ROOT, file.upload_to, now.year, now.month, now.day)
                filename = generate_file_name(path, serializer.validated_data[file_name].filename)

                with open('/'.join([path, filename]), 'wb') as f:
                    while True:
                        chunk = serializer.validated_data[file_name].file.readline(CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)

                url = '{scheme}://{host}/{media_url}/{upload_to}{y}/{m}/{d}/{file_name}' \
                      .format(scheme=self.request.scheme, host=self.request.host, media_url=MEDIA_URL,
                              upload_to=file.upload_to + '/' if file.upload_to is not None else '',
                              y=now.year, m=now.month, d=now.day, file_name=filename)
                serializer.validated_data[file_name] = url

            query = model.insert().values(**serializer.validated_data)
            insert = await conn.execute(query)

            queryset = model.c.id == insert.lastrowid
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data, status=201)


async def get_json_data(request):
    if not request.can_read_body:
        return {}

    data = await request.json()
    return data


async def get_multipart_data(request):
    data = {}

    reader = await request.multipart()
    field = await reader.next()
    while field is not None:
        content_type = field.headers.get(hdrs.CONTENT_TYPE)

        if field.filename:
            tmp = tempfile.TemporaryFile()
            chunk = await field.read_chunk(size=2 ** 16)
            while chunk:
                chunk = field.decode(chunk)
                tmp.write(chunk)
                chunk = await field.read_chunk(size=2 ** 16)
            tmp.seek(0)

            ff = FileField(field.name, field.filename,
                           tmp, content_type, field.headers)
            data[field.name] = ff
        else:
            value = await field.read(decode=True)
            if content_type is None or \
                    content_type.startswith('text/'):
                charset = field.get_charset(default='utf-8')
                value = value.decode(charset)
            data[field.name] = value

        field = await reader.next()
    return data


async def validate_request_data(request, *args):
    data = await get_json_data(request)
    errors = {}
    msg = 'This field is required'

    for arg in args:
        if data.get(arg) is None:
            errors[arg] = msg

    if errors:
        raise ValidationError(errors)

    return data
