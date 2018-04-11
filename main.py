from aiohttp import web

from project import settings

if __name__ == '__main__':
    app = web.Application()
    web.run_app(app, host=settings.HOST, port=settings.PORT)
