from aiohttp import web

from project import settings
from utils.exceptions import PermissionDenied


def setup_middlewares(app):
    app.middlewares.append(check_permissions)


@web.middleware
async def check_permissions(request, handler):
    if hasattr(handler, 'get_permission_classes'):
        permissions = handler.get_permission_classes(request)
    else:
        permissions = getattr(handler, 'permission_classes', settings.DEFAULT_PERMISSION_CLASSES)

    for permission in permissions:
        perm = permission()
        try:
            assert await perm.has_permission(request)
        except AssertionError:
            raise PermissionDenied
    resp = await handler(request)
    return resp
