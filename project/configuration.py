import aiohttp_cors

from project.db import init_mysql, close_mysql
from project.middlewares import setup_middlewares
from project.routes import setup_routes


def configure_app(app):
    app.on_startup.append(init_mysql)
    app.on_cleanup.append(close_mysql)

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
