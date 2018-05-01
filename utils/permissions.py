from apps.users.models import User
from utils.exceptions import Unauthorized


class BasePermission(object):
    async def has_permission(self, request):
        raise NotImplementedError


class AllowAny(BasePermission):
    async def has_permission(self, request):
        return True


class IsAuthenticated(BasePermission):
    async def has_permission(self, request):
        header = request.headers.get('AUTHORIZATION')
        if header is None or not header.lower().startswith('token'):
            raise Unauthorized

        redis = request.app['redis']
        token = header[6:]

        users = await redis.keys('users:*')
        for user in users:
            t = await redis.hget(user, 'token')
            if t == token:
                user_id = int(user[6:])
                async with request.app['db'].acquire() as conn:
                    query = User.select().where(User.c.id == user_id)
                    users = await conn.execute(query)
                    user = await users.fetchone()
                    request['user'] = user
                    return True

        raise Unauthorized(dict(detail='Invalid token'))


def permission_classes(permissions):
    def decorator(func):
        func.permission_classes = permissions
        return func
    return decorator
