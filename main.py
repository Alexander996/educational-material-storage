from aiohttp import web

from project import settings
from project.configuration import configure_app

if __name__ == '__main__':
    app = web.Application()
    configure_app(app)
    web.run_app(app, host=settings.HOST, port=settings.PORT)
