import binascii
import os

from aiohttp import web

from apps.users.models import User
from utils.auth_token.serializers import AuthTokenSerializer
from utils.exceptions import ValidationError
from utils.permissions import AllowAny
from utils.views import BaseView, get_json_data


class AuthTokenView(BaseView):
    _detail = True
    model = User
    serializer_class = AuthTokenSerializer
    permission_classes = [AllowAny]

    async def post(self):
        async with self.request.app['db'].acquire() as conn:
            redis = self.request.app['redis']
            data = await get_json_data(self.request)
            serializer = self.serializer_class(data=data)
            serializer.create_validate()
            queryset = (User.c.username == serializer.validated_data['username']) &\
                       (User.c.password == serializer.validated_data['password'])

            query = self.build_query('select', queryset=queryset)
            users = await conn.execute(query)
            if users.rowcount == 0:
                raise ValidationError(dict(detail='Invalid username or password'))

            user = await users.fetchone()
            redis_user = 'users:{}'.format(user.id)

            token = await redis.hget(redis_user, 'token')
            if token is None:
                await redis.hset(redis_user, 'token', generate_token())
                token = await redis.hget(redis_user, 'token')

            return web.json_response(dict(token=token))


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()
