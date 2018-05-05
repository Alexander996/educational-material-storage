from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

from project.configuration import configure_app


class BaseTestCase(AioHTTPTestCase):
    async def get_application(self):
        app = web.Application()
        configure_app(app, testing=True)
        return app


class AioTestCase(BaseTestCase):
    async def setUpAsync(self):
        data = {
            'username': 'admin',
            'password': 'adminsuperuser'
        }

        resp = await self.client.request('POST', '/api/login/', json=data)
        body = await resp.json()
        token = body['token']
        self.headers = {
            'authorization': 'Token {}'.format(token),
            'content_type': 'application/json'
        }
