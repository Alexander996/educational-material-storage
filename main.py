from aiohttp import web

from project import settings
from project.db import init_mysql, init_redis, close_mysql, close_redis

if __name__ == '__main__':
    app = web.Application()

    app.on_startup.append(init_mysql)
    app.on_startup.append(init_redis)

    app.on_cleanup.append(close_mysql)
    app.on_cleanup.append(close_redis)

    web.run_app(app, host=settings.HOST, port=settings.PORT)
