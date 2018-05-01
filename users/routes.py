from aiohttp import web

from users.views import UsersView, UserView
from utils.auth_token.views import AuthTokenView


def setup_routes(app):
    app.add_routes([
        web.view('/users/', UsersView),
        web.view(r'/users/{pk:\d+}/', UserView),
        web.view('/login/', AuthTokenView),
    ])
