from aiomysql.sa import create_engine
from aioredis import create_redis

from project.settings import DATABASE, REDIS


# Connections initialization
async def init_mysql(app):
    mysql_engine = await create_engine(**DATABASE)
    app['db'] = mysql_engine


async def init_redis(app):
    redis_engine = await create_redis(**REDIS)
    app['redis'] = redis_engine


# Closing connections
async def close_mysql(app):
    app['db'].close()
    await app['db'].wait_closed()


async def close_redis(app):
    app['redis'].close()
    await app['redis'].wait_closed()
