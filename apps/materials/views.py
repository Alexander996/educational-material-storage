import json

from datetime import datetime

from aiohttp import web

from apps.materials.models import Material, MaterialCategory
from apps.materials.serializers import MaterialSerializer
from project.settings import MEDIA_URL, MEDIA_ROOT, CHUNK_SIZE
from utils import views
from utils.exceptions import ValidationError
from utils.media import generate_path_to_file, generate_file_name
from utils.views import get_multipart_data

material_routes = web.RouteTableDef()


@material_routes.view('/api/materials/')
class MaterialsView(views.ListView):
    model = Material
    serializer_class = MaterialSerializer

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

                url = '{scheme}://{host}/{media_url}/{upload_to}{y}/{m}/{d}/{file_name}' \
                      .format(scheme=self.request.scheme, host=self.request.host, media_url=MEDIA_URL,
                              upload_to=file.upload_to + '/' if file.upload_to is not None else '',
                              y=now.year, m=now.month, d=now.day, file_name=filename)
                serializer.validated_data[file_name] = url

            trans = await conn.begin()
            try:
                categories = serializer.validated_data.pop('categories')
                query = model.insert().values(**serializer.validated_data)
                insert = await conn.execute(query)

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
