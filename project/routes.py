from aiohttp import web

from apps.users.views import user_routes
from utils.auth_token.views import AuthTokenView


def setup_routes(app):
    app.add_routes([
        web.view('/api/login/', AuthTokenView)
    ])

    app.add_routes(user_routes)
