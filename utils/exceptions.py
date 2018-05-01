import json

from aiohttp.web_exceptions import HTTPException
from aiohttp.web_response import Response


class BaseHTTPException(HTTPException):
    default_msg = None
    status = None

    def __init__(self, data=None):
        if data is None:
            data = self.default_msg
        data = json.dumps(data)
        Response.__init__(self, text=data, status=self.status, content_type='application/json')
        Exception.__init__(self)


class ValidationError(BaseHTTPException):
    default_msg = {'detail': 'Bad request'}
    status = 400


class Unauthorized(BaseHTTPException):
    default_msg = {'detail': 'Authentication credentials were not provided'}
    status = 401


class PermissionDenied(BaseHTTPException):
    default_msg = {'detail': 'You do not have permissions to perform this action'}
    status = 403
