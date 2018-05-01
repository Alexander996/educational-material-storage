from project.db import init_mysql, init_redis, close_mysql, close_redis
from project.middlewares import setup_middlewares
from project.routes import setup_routes


def configure_app(app):
    app.on_startup.append(init_mysql)
    app.on_startup.append(init_redis)

    app.on_cleanup.append(close_mysql)
    app.on_cleanup.append(close_redis)

    setup_routes(app)
    setup_middlewares(app)
