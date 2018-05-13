from apps.users.models import User
from utils.auth_token.models import Token
from utils.exceptions import Unauthorized, PermissionDenied


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

        token = header[6:]
        async with request.app['db'].acquire() as conn:
            query = Token.select().where(Token.c.key == token)
            result = await conn.execute(query)
            if result.rowcount == 0:
                raise Unauthorized(dict(detail='Invalid token'))
            else:
                token = await result.fetchone()
                query = User.select().where(User.c.id == token.user)
                result = await conn.execute(query)
                user = await result.fetchone()
                if user.blocked:
                    raise PermissionDenied(dict(detail='User is blocked'))
                request['user'] = user
                return True


def permission_classes(permissions):
    def decorator(func):
        func.permission_classes = permissions
        return func
    return decorator
