import argparse
import logging

from aiohttp import web

from project import settings
from project.configuration import configure_app

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description="aiohttp server example")
parser.add_argument('--path')
parser.add_argument('--port')


if __name__ == '__main__':

    app = web.Application()
    configure_app(app)
    args = parser.parse_args()
    web.run_app(app, path=args.path, port=args.port)
