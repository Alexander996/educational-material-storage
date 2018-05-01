from json import JSONDecodeError

from aiohttp import web

from apps.users.models import User

from apps.users.serializers import UserSerializer
from project.permissions import IsAdmin
from utils import views
from utils.exceptions import ValidationError
from utils.permissions import AllowAny, permission_classes, IsAuthenticated

user_routes = web.RouteTableDef()


@user_routes.view('/api/users/')
class UsersView(views.ListView):
    model = User
    serializer_class = UserSerializer

    @staticmethod
    def get_permission_classes(request):
        if request.method == 'POST':
            return [AllowAny]
        else:
            return [IsAuthenticated]

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

    @staticmethod
    def get_permission_classes(request):
        if request.method == 'GET':
            return [IsAuthenticated]
        else:
            return [IsAdmin]


@user_routes.post(r'/api/users/{pk:\d+}/block/')
@permission_classes([IsAdmin])
async def block_user(request):
    return await change_user_status(request, blocked=True)


@user_routes.post(r'/api/users/{pk:\d+}/unblock/')
@permission_classes([IsAdmin])
async def unblock_user(request):
    return await change_user_status(request, blocked=False)


async def change_user_status(request, blocked=False):
    async with request.app['db'].acquire() as conn:
        pk = request.match_info['pk']
        query = User.update().where(User.c.id == pk).values(blocked=blocked)
        await conn.execute(query)
        return web.Response()


@user_routes.post('/api/users/check_username/')
@permission_classes([AllowAny])
async def check_username(request):
    return await check_user_field(request, field_name='username')


@user_routes.post('/api/users/check_email/')
@permission_classes([AllowAny])
async def check_email(request):
    return await check_user_field(request, field_name='email')


async def check_user_field(request, field_name):
    async with request.app['db'].acquire() as conn:
        try:
            data = await request.json()
        except JSONDecodeError:
            data = {}

        field = data.get(field_name)
        if field is None:
            raise ValidationError({field_name: 'This field is required'})

        attr = getattr(User.c, field_name)
        query = User.select().where(attr == field)
        users = await conn.execute(query)
        if users.rowcount == 0:
            return web.json_response(dict(detail='{} свободен'.format(field_name)))
        else:
            return web.json_response(dict(detail='Пользователь с таким {} уже существует'.format(field_name)),
                                     status=400)
