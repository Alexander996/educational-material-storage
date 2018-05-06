from apps.materials.models import Material
from apps.users.serializers import UserSerializer
from utils import serializers


class MaterialSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ('auto_date', 'deleted')

    async def is_valid(self, method, partial=False):
        await super(MaterialSerializer, self).is_valid(method, partial=partial)
        self.validated_data['owner'] = self.context['request']['user'].id
