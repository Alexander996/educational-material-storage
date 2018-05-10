import os

from utils.pagination import PagePagination
from utils.permissions import IsAuthenticated

HOST = '127.0.0.1'
PORT = 8080


DATABASE = {
    'user': 'storage',
    'db': 'material_storage_db',
    'host': '127.0.0.1',
    'password': 'storagedb',
    'autocommit': True,
    'charset': 'utf8',
}

REDIS = {
    'address': 'redis://localhost',
    'encoding': 'utf-8',
}


DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]
DEFAULT_PAGINATION_CLASS = PagePagination
PAGE_LIMIT = 20


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media'


CHUNK_SIZE = 8192
