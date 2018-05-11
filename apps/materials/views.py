import json
import os

from datetime import datetime

from aiohttp import web

from apps.materials.models import Material, MaterialCategory, MaterialUser
from apps.materials.serializers import MaterialSerializer
from project import settings
from project.permissions import MODERATOR
from project.settings import MEDIA_URL, MEDIA_ROOT, CHUNK_SIZE, BASE_DIR
from utils import views
from utils.exceptions import ValidationError, PermissionDenied
from utils.media import generate_path_to_file, generate_file_name
from utils.pagination import PagePagination
from utils.views import get_multipart_data

material_routes = web.RouteTableDef()


@material_routes.view('/api/materials/')
class MaterialsView(views.ListView):
    model = Material
    serializer_class = MaterialSerializer

    async def get(self):
        async with self.request.app['db'].acquire() as conn:
            serializer = self.get_serializer(many=True)
            queryset = await get_queryset_by_user(self.request, conn)
            query = self.build_query('select', queryset=queryset)
            paginator = self.get_pagination_class()
            if paginator is not None:
                await paginator.check_next_page(query)
                query = paginator.paginate_query(query)

            result = await conn.execute(query)
            data = await serializer.to_json(result)
            if paginator is not None:
                data = paginator.get_paginated_data(data)
            return web.json_response(data)

    async def multipart_post(self):
        async with self.request.app['db'].acquire() as conn:
            now = datetime.now()
            model = self.get_model()
            if self.request.can_read_body:
                data = await get_multipart_data(self.request)
            else:
                data = {}

            try:
                data['categories'] = json.loads(data['categories']) if data['categories'] else []
            except json.decoder.JSONDecodeError:
                raise ValidationError(dict(categories='JSON decode error'))

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

                url = '/{media_url}/{upload_to}{y}/{m}/{d}/{file_name}' \
                      .format(media_url=MEDIA_URL, upload_to=file.upload_to + '/' if file.upload_to is not None else '',
                              y=now.year, m=now.month, d=now.day, file_name=filename)
                serializer.validated_data[file_name] = url
                index = filename.rfind('.')
                serializer.validated_data['extension'] = filename[index+1:].upper()

            trans = await conn.begin()
            try:
                categories = serializer.validated_data.pop('categories')
                query = model.insert().values(**serializer.validated_data)
                insert = await conn.execute(query)

                query = MaterialUser.insert().values(material=insert.lastrowid,
                                                     user=self.request['user'].id)
                await conn.execute(query)

                for category in categories:
                    query = MaterialCategory.insert().values(material=insert.lastrowid,
                                                             category=category['category'].id)
                    await conn.execute(query)
            except Exception as e:
                await trans.rollback()
                return web.json_response(dict(exception=e.__class__.__name__, detail=e.args))
            else:
                await trans.commit()

            queryset = model.c.id == insert.lastrowid
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data, status=201)


@material_routes.view(r'/api/materials/{pk:\d+}/')
class MaterialView(views.DetailView):
    model = Material
    serializer_class = MaterialSerializer

    async def delete(self):
        async with self.request.app['db'].acquire() as conn:
            queryset = self.get_queryset()
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            material = await result.fetchone()
            if material.owner != self.request['user'].id and self.request['user'].role < MODERATOR:
                raise PermissionDenied

            query = self.build_query('update', values=dict(deleted=True), queryset=queryset)
            await conn.execute(query)

            query = MaterialUser.delete().where(MaterialUser.c.material == material.id)
            await conn.execute(query)

            index = material.file.find(MEDIA_URL)
            if index != -1:
                path = BASE_DIR + '/' + material.file[index:]

                try:
                    os.remove(path)
                except FileNotFoundError:
                    pass

            return web.Response(status=204)


@material_routes.get('/api/materials/search/')
async def search_materials(request):
    async with request.app['db'].acquire() as conn:
        text = request.query.get('text')
        if text is None:
            raise ValidationError(dict(text='This query parameters is required'))

        queryset = await get_queryset_by_user(request, conn)
        like = '%{}%'.format(text)
        queryset &= ((Material.c.name.like(like)) |
                     (Material.c.author.like(like)))

        query = Material.select().where(queryset)
        paginator = PagePagination(settings.PAGE_LIMIT, request)
        await paginator.check_next_page(query)
        query = paginator.paginate_query(query)
        result = await conn.execute(query)

        serializer = MaterialSerializer(many=True, context={'request': request})
        data = await serializer.to_json(result)
        data = paginator.get_paginated_data(data)
        return web.json_response(data)


async def get_queryset_by_user(request, conn):
    owner = request.query.get('owner')
    if owner is None or request['user'].id != int(owner):
        queryset = (Material.c.is_open == True) & (Material.c.deleted == False)
    else:
        queryset = None

    if owner is not None:
        query = MaterialUser.select().where(MaterialUser.c.user == owner)
        material_users = await conn.execute(query)
        materials = None
        async for material_user in material_users:
            if materials is not None:
                materials |= (Material.c.id == material_user.material)
            else:
                materials = (Material.c.id == material_user.material)

        if queryset is not None:
            queryset &= materials
        else:
            queryset = materials

    return queryset
