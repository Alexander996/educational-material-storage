import argparse
import logging

from aiohttp import web

from project import settings
from project.configuration import configure_app

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description="Educational material storage server")
parser.add_argument('--path', help='Path to unix socket')
parser.add_argument('--port')
parser.add_argument('--host')


if __name__ == '__main__':

    app = web.Application()
    configure_app(app)

    args = parser.parse_args()
    path = args.path
    host = args.host
    port = args.port

    if path is None:
        if host is None:
            host = settings.HOST
        if port is None:
            port = settings.PORT

    web.run_app(app, path=path, host=host, port=port)
