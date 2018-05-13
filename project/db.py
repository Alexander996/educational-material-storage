from aiomysql.sa import create_engine
from project import settings

from utils.db import CurrentDBConnection


async def init_mysql(app):
    mysql_engine = await create_engine(**settings.DATABASE)
    app['db'] = mysql_engine
    CurrentDBConnection.set_db_connection(mysql_engine)


async def close_mysql(app):
    app['db'].close()
    await app['db'].wait_closed()
