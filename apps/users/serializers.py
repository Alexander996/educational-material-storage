from apps.users.models import User, Registration
from utils import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.PasswordField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = Registration
        exclude = ('is_completed',)


class UserCreateSerializer(serializers.Serializer):
    registration = serializers.ForeignKeyField(model=Registration)
    role = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        exclude = ('password',)
        read_only_fields = ('blocked',)
