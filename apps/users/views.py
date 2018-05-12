from aiohttp import web
from aiohttp.web_exceptions import HTTPMethodNotAllowed
from sqlalchemy import desc

from apps.users.models import User, Registration

from apps.users.serializers import UserSerializer, RegistrationSerializer, UserCreateSerializer
from project import settings
from project.permissions import IsModeratorOrAbove, MODERATOR
from utils import views
from utils.exceptions import ValidationError, PermissionDenied
from utils.hash import hash_password
from utils.pagination import PagePagination
from utils.permissions import AllowAny, permission_classes, IsAuthenticated
from utils.views import get_json_data, validate_request_data

user_routes = web.RouteTableDef()


@user_routes.view('/api/registration/')
class RegistrationView(views.ListView):
    model = Registration
    serializer_class = RegistrationSerializer
    queryset = Registration.c.is_completed == False
    order_by = desc('id')

    @staticmethod
    def get_permission_classes(request):
        if request.method == 'POST':
            return [AllowAny]
        else:
            return [IsModeratorOrAbove]


@user_routes.view(r'/api/registration/{pk:\d+}/')
class RegistrationPkView(views.DetailView):
    model = Registration
    serializer_class = RegistrationSerializer

    async def put(self):
        raise HTTPMethodNotAllowed

    async def patch(self):
        raise HTTPMethodNotAllowed


@user_routes.view('/api/users/')
class UsersView(views.ListView):
    model = User
    serializer_class = UserSerializer

    @staticmethod
    def get_permission_classes(request):
        if request.method == 'POST':
            return [IsModeratorOrAbove]
        else:
            return [IsAuthenticated]

    def get_queryset(self):
        return get_users_by_filter(self.request)

    async def post(self):
        async with self.request.app['db'].acquire() as conn:
            model = self.get_model()
            request_data = await get_json_data(self.request)
            serializer = UserCreateSerializer(data=request_data)
            await serializer.create_validate()

            registration = serializer.validated_data['registration']
            if registration.is_completed:
                raise ValidationError(dict(detail='Registration is already completed'))

            data = {
                'username': registration.username,
                'password': registration.password,
                'email': registration.email,
                'first_name': registration.first_name,
                'last_name': registration.last_name,
                'role': serializer.validated_data['role']
            }

            query = self.build_query('create', values=data)
            insert = await conn.execute(query)

            query = Registration.update().where(Registration.c.id == registration.id).values(is_completed=True)
            await conn.execute(query)

            queryset = model.c.id == insert.lastrowid
            query = self.build_query('select', queryset=queryset)
            result = await conn.execute(query)

            serializer = UserSerializer()
            data = await serializer.to_json(result)
            return web.json_response(data, status=201)


@user_routes.view(r'/api/users/{pk:\d+}/')
class UserView(views.DetailView):
    model = User
    serializer_class = UserSerializer

    async def put(self):
        self.check_permissions()
        return await super(UserView, self).put()
    
    async def patch(self):
        self.check_permissions()
        return await super(UserView, self).patch()

    def check_permissions(self):
        user = self.request['user']
        if user.role < MODERATOR:
            pk = self.request.match_info['pk']
            if int(pk) != user.id:
                raise PermissionDenied

    async def delete(self):
        raise HTTPMethodNotAllowed


@user_routes.post(r'/api/users/{pk:\d+}/change_password/')
@permission_classes([IsAuthenticated])
async def change_password(request):
    async with request.app['db'].acquire() as conn:
        pk = request.match_info['pk']
        if int(pk) != request['user'].id:
            raise PermissionDenied

        data = await validate_request_data(request, 'password')
        password = data['password']

        query = User.update().where(User.c.id == pk).values(password=hash_password(password))
        await conn.execute(query)
        return web.Response()


@user_routes.post(r'/api/users/{pk:\d+}/block/')
@permission_classes([IsModeratorOrAbove])
async def block_user(request):
    return await change_user_status(request, blocked=True)


@user_routes.post(r'/api/users/{pk:\d+}/unblock/')
@permission_classes([IsModeratorOrAbove])
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
        data = await validate_request_data(request, field_name)
        field = data[field_name]

        attr = getattr(User.c, field_name)
        query = User.select().where(attr == field)
        users = await conn.execute(query)
        if users.rowcount == 0:
            await users.close()
            return web.json_response(dict(free=True))
        else:
            await users.close()
            return web.json_response(dict(free=False))


@user_routes.get('/api/users/search/')
async def search_users(request):
    async with request.app['db'].acquire() as conn:
        text = request.query.get('text')
        if text is None:
            raise ValidationError(dict(text='This query parameters is required'))

        like = '%{}%'.format(text)
        queryset = ((User.c.username.like(like)) |
                    (User.c.first_name.like(like)) |
                    (User.c.last_name.like(like)))

        queryset &= get_users_by_filter(request)
        print('QUERYSET:', queryset)
        query = User.select().where(queryset)
        paginator = PagePagination(settings.PAGE_LIMIT, request)
        await paginator.check_next_page(query)
        query = paginator.paginate_query(query)
        result = await conn.execute(query)

        serializer = UserSerializer(many=True, context={'request': request})
        data = await serializer.to_json(result)
        data = paginator.get_paginated_data(data)
        return web.json_response(data)


def get_users_by_filter(request):
    blocked = request.query.get('blocked')
    if blocked is not None and blocked.lower() == 'true':
        queryset = User.c.blocked == True
    else:
        queryset = User.c.blocked == False

    roles = request.query.getall('role', [])
    roles_queryset = None
    for role in roles:
        if roles_queryset is not None:
            roles_queryset |= (User.c.role == role)
        else:
            roles_queryset = (User.c.role == role)

    if roles_queryset is not None:
        queryset &= roles_queryset
    return queryset
