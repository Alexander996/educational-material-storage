from users.models import User
from utils import fields
from utils.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    password = fields.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
