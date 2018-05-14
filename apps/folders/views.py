from aiohttp import web

from apps.folders.models import Folder, FolderMaterial
from apps.folders.serializers import FolderSerializer, FolderDetailSerializer
from utils import views
from utils.exceptions import PermissionDenied

folder_routes = web.RouteTableDef()


@folder_routes.view('/api/folders/')
class FoldersView(views.ListView):
    model = Folder
    serializer_class = FolderSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.query.get('user', self.request['user'].id)
        parent = self.request.query.get('parent')
        queryset = (Folder.c.user == user) & (Folder.c.parent == parent)
        if int(user) != self.request['user'].id:
            queryset &= Folder.c.is_open == True
        return queryset


@folder_routes.view(r'/api/folders/{pk:\d+}/')
class FolderView(views.DetailView):
    model = Folder

    def get_queryset(self):
        user = self.request.query.get('user', self.request['user'].id)
        pk = self.request.match_info['pk']
        queryset = (Folder.c.user == user) & (Folder.c.id == pk)
        if int(user) != self.request['user'].id:
            queryset &= Folder.c.is_open == True
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FolderDetailSerializer
        else:
            return FolderSerializer

    async def _update(self, partial=False):
        async with self.request.app['db'].acquire() as conn:
            queryset = self.get_queryset()
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)
            folder = await result.fetchone()
            if folder.user != self.request['user'].id:
                raise PermissionDenied
            return await super(FolderView, self)._update(partial=partial)

    async def delete(self):
        async with self.request.app['db'].acquire() as conn:
            pk = self.request.match_info['pk']
            query = Folder.select().where(Folder.c.id == pk)
            result = await conn.execute(query)
            folder = await result.fetchone()
            if folder.user != self.request['user'].id:
                raise PermissionDenied

            query = FolderMaterial.delete().where((FolderMaterial.c.folder == pk) &
                                                  (FolderMaterial.c.user == self.request['user'].id))
            await conn.execute(query)

            queryset = self.get_queryset()
            query = self.build_query('delete', queryset=queryset)
            await conn.execute(query)
            return web.Response(status=204)
