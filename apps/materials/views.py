from datetime import datetime

from aiohttp import web

from apps.materials.models import Material
from apps.materials.serializers import MaterialSerializer
from project.settings import MEDIA_URL, MEDIA_ROOT
from utils import views
from utils.media import generate_path_to_file, generate_file_name

material_routes = web.RouteTableDef()


@material_routes.view('/api/materials/')
class MaterialsView(views.ListView):
    model = Material
    serializer_class = MaterialSerializer

    async def post(self):
        data = {}
        now = datetime.now()

        if self.request.can_read_body:
            reader = await self.request.multipart()
            field = await reader.next()

            while field is not None:
                if field.name == 'file':
                    path = generate_path_to_file(MEDIA_ROOT, 'materials', now.year, now.month, now.day)
                    filename = generate_file_name(path, field.filename)

                    with open('/'.join([path, filename]), 'wb') as f:
                        while True:
                            chunk = await field.read_chunk()
                            if not chunk:
                                break
                            f.write(chunk)

                    url = '{scheme}://{host}/{media_url}/{date}{file_name}' \
                          .format(scheme=self.request.scheme, host=self.request.host, media_url=MEDIA_URL,
                                  date=now.strftime('%Y/%m/%d/'), file_name=filename)
                    data[field.name] = url
                else:
                    data[field.name] = await field.text()
                field = await reader.next()

        serializer = self.get_serializer(data=data)
        await serializer.create_validate()

        async with self.request.app['db'].acquire() as conn:
            query = Material.insert().values(**serializer.validated_data)
            insert = await conn.execute(query)

            queryset = Material.c.id == insert.lastrowid
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            data = await serializer.to_json(result)
            return web.json_response(data, status=201)
