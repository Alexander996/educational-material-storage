from aiohttp import web

from apps.folders.models import Folder
from apps.folders.serializers import FolderSerializer, FolderDetailSerializer
from utils import views

folder_routes = web.RouteTableDef()


@folder_routes.view('/api/folders/')
class FoldersView(views.ListView):
    model = Folder
    serializer_class = FolderSerializer
    pagination_class = None

    def get_queryset(self):
        parent = self.request.query.get('parent')
        return (Folder.c.user == self.request['user'].id) & (Folder.c.parent == parent)


@folder_routes.view(r'/api/folders/{pk:\d+}/')
class FolderView(views.DetailView):
    model = Folder

    def get_queryset(self):
        pk = self.request.match_info['pk']
        return (Folder.c.user == self.request['user'].id) & (Folder.c.id == pk)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FolderDetailSerializer
        else:
            return FolderSerializer
