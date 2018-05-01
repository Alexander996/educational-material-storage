from aiohttp import web

from apps.users.models import User

from apps.users.serializers import UserSerializer
from utils import views

user_routes = web.RouteTableDef()


@user_routes.view('/api/users/')
class UsersView(views.ListView):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        blocked = self.request.query.get('blocked')
        if blocked is not None and blocked.lower() == 'true':
            return User.c.blocked == True
        else:
            return User.c.blocked == False


@user_routes.view(r'/api/users/{pk:\d+}/')
class UserView(views.DetailView):
    model = User
    serializer_class = UserSerializer


@user_routes.post(r'/api/users/{pk:\d+}/block/')
async def block_user(request):
    await change_user_status(request, blocked=True)
    return web.Response()


@user_routes.post(r'/api/users/{pk:\d+}/unblock/')
async def unblock_user(request):
    await change_user_status(request, blocked=False)
    return web.Response()


async def change_user_status(request, blocked=False):
    async with request.app['db'].acquire() as conn:
        pk = request.match_info['pk']
        query = User.update().where(User.c.id == pk).values(blocked=blocked)
        await conn.execute(query)
