import copy
from aiomysql.sa import create_engine
from aioredis import create_redis
from project import settings

from utils.db import CurrentDBConnection


# Connections initialization
async def init_mysql(app):
    mysql_engine = await create_engine(**settings.DATABASE)
    app['db'] = mysql_engine
    CurrentDBConnection.set_db_connection(mysql_engine)


async def test_init_mysql(app):
    db_settings = copy.deepcopy(settings.DATABASE)
    db_settings['autocommit'] = False
    mysql_engine = await create_engine(**db_settings)
    app['db'] = mysql_engine
    CurrentDBConnection.set_db_connection(mysql_engine)


async def init_redis(app):
    redis_engine = await create_redis(**settings.REDIS)
    app['redis'] = redis_engine


# Closing connections
async def close_mysql(app):
    app['db'].close()
    await app['db'].wait_closed()


async def close_redis(app):
    app['redis'].close()
    await app['redis'].wait_closed()
