import aiohttp_cors

from project.db import init_mysql, init_redis, close_mysql, close_redis, test_init_mysql
from project.middlewares import setup_middlewares
from project.routes import setup_routes


def configure_app(app, testing=False):
    if testing:
        app.on_startup.append(test_init_mysql)
    else:
        app.on_startup.append(init_mysql)

    app.on_startup.append(init_redis)

    app.on_cleanup.append(close_mysql)
    app.on_cleanup.append(close_redis)

    setup_routes(app)
    setup_middlewares(app)

    cors = aiohttp_cors.setup(app, defaults={
        '*': aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers='*',
            allow_headers='*',
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)
