from utils import fields
from utils.serializers import Serializer


class AuthTokenSerializer(Serializer):
    username = fields.CharField()
    password = fields.PasswordField()
