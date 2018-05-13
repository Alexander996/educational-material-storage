import binascii
import os

from aiohttp import web

from apps.users.models import User
from apps.users.serializers import UserSerializer
from utils.auth_token.models import Token
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
            data = await get_json_data(self.request)
            serializer = self.serializer_class(data=data)
            await serializer.create_validate()
            queryset = (User.c.username == serializer.validated_data['username']) &\
                       (User.c.password == serializer.validated_data['password'])

            query = self.build_query('select', queryset=queryset)
            users = await conn.execute(query)
            if users.rowcount == 0:
                raise ValidationError(dict(detail='Invalid username or password'))

            serializer = UserSerializer()
            user_data = await serializer.to_json(users)
            if user_data['blocked']:
                raise ValidationError(dict(detail='User is blocked'))

            query = Token.select().where(Token.c.user == user_data['id'])
            result = await conn.execute(query)
            if result.rowcount == 0:
                key = generate_token()
                query = Token.insert().values(key=key, user=user_data['id'])
                await conn.execute(query)
            else:
                token = await result.fetchone()
                key = token.key

            resp = dict(token=key)
            resp.update(user_data)
            return web.json_response(resp)


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()
