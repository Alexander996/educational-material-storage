from utils import fields
from utils.serializers import Serializer


class UserSerializer(Serializer):
    id = fields.IntegerField(read_only=True)
    username = fields.CharField()
    password = fields.CharField(write_only=True)
    first_name = fields.CharField(required=False)
    last_name = fields.CharField(required=False)
    role = fields.IntegerField()
