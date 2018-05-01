from apps.users.models import User
from utils import fields
from utils.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    password = fields.PasswordField(write_only=True)
    email = fields.EmailField()
    blocked = fields.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
