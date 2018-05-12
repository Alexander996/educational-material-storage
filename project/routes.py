from aiohttp import web

from apps.categories.views import category_routes
from apps.folders.views import folder_routes
from apps.materials.views import material_routes
from apps.users.views import user_routes
from utils.auth_token.views import AuthTokenView


def setup_routes(app):
    app.add_routes([
        web.view('/api/login/', AuthTokenView)
    ])

    app.add_routes(user_routes)
    app.add_routes(category_routes)
    app.add_routes(material_routes)
    app.add_routes(folder_routes)
