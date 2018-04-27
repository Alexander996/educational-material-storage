import json

from aiohttp.web_exceptions import HTTPException
from aiohttp.web_response import Response


class ValidationError(HTTPException):
    def __init__(self, data):
        data = json.dumps(data)
        Response.__init__(self, text=data, status=400, content_type='application/json')
        Exception.__init__(self)
