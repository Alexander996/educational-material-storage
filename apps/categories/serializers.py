from apps.categories.models import Category
from utils import fields
from utils.serializers import ModelSerializer


class CategorySerializer(ModelSerializer):
    deleted = fields.BooleanField(read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
