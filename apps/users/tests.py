from aiohttp.test_utils import unittest_run_loop

from project.tests import BaseTestCase, AioTestCase


class LoginTestCase(BaseTestCase):
    @unittest_run_loop
    async def test_login(self):
        data = {
            'username': 'admin',
            'password': 'adminsuperuser'
        }

        resp = await self.client.request('POST', '/api/login/', json=data)
        self.assertEqual(resp.status, 200)


class RegistrationTestCase(AioTestCase):
    @unittest_run_loop
    async def test_create_registration(self):
        data = {
            'username': 'test_user',
            'password': 'test_user',
            'email': 'test_email@mail.com',
            'first_name': 'test_user',
            'last_name': 'test_user'
        }

        resp = await self.client.request('POST', '/api/registration/', json=data)
        self.assertEqual(resp.status, 201)

    @unittest_run_loop
    async def test_get_registrations(self):
        resp = await self.client.request('GET', '/api/registration/', headers=self.headers)
        self.assertEqual(resp.status, 200)


class UserTestCase(AioTestCase):
    @unittest_run_loop
    async def test_get_users(self):
        resp = await self.client.request('GET', '/api/users/', headers=self.headers)
        self.assertEqual(resp.status, 200)

    @unittest_run_loop
    async def test_get_user(self):
        resp = await self.client.request('GET', '/api/users/1/', headers=self.headers)
        self.assertEqual(resp.status, 200)
