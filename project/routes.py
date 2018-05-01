from aiohttp import web

from apps.users.views import UsersView, UserView
from utils.auth_token.views import AuthTokenView


def setup_routes(app):
    app.add_routes([
        web.view('/api/login/', AuthTokenView),
        web.view('/api/users/', UsersView),
        web.view(r'/api/users/{pk:\d+}/', UserView),
    ])
