import asyncio

from aiomysql.sa import create_engine

from apps.users.models import User
from project.permissions import ADMIN
from project.settings import DATABASE
from utils.hash import hash_password


async def create_admin():
    mysql_engine = await create_engine(**DATABASE)
    async with mysql_engine.acquire() as conn:
        data = {
            'username': 'admin',
            'password': hash_password('adminsuperuser'),
            'email': 'admin@gmail.com',
            'first_name': 'Админ',
            'last_name': 'Админ',
            'role': ADMIN
        }

        query = User.insert().values(**data)
        await conn.execute(query)
        print('Admin created')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_admin())
    loop.close()
