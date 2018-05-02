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
PAGE_LIMIT = 10
