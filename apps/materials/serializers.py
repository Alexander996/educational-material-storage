from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer
from apps.materials.models import Material, MaterialCategory, MaterialUser
from apps.users.serializers import UserSerializer
from utils import serializers


class MaterialCategorySerializer(serializers.Serializer):
    category = serializers.ForeignKeyField(model=Category)

    async def to_json(self, result):
        json = await super(MaterialCategorySerializer, self).to_json(result)
        async with self.context['request'].app['db'].acquire() as conn:
            query = Category.select().where(Category.c.id == json['category'])
            result = await conn.execute(query)
            serializer = CategorySerializer()
            category = await serializer.to_json(result)
            json = category
            return json


class MaterialSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    file = serializers.FileField(upload_to='materials')
    categories = MaterialCategorySerializer(many=True)

    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ('auto_date', 'deleted', 'extension')

    async def is_valid(self, method, partial=False):
        await super(MaterialSerializer, self).is_valid(method, partial=partial)
        self.validated_data['owner'] = self.context['request']['user'].id

    async def to_json(self, result):
        json = await super(MaterialSerializer, self).to_json(result)
        request = self.context['request']
        json['file'] = '{scheme}://{host}{path}'.format(scheme=request.scheme,
                                                        host=request.host,
                                                        path=json['file'])

        async with request.app['db'].acquire() as conn:
            query = MaterialCategory.select().where(MaterialCategory.c.material == json['id'])
            result = await conn.execute(query)
            serializer = MaterialCategorySerializer(many=True, context=self.context)
            categories = await serializer.to_json(result)
            json['categories'] = categories

            query = MaterialUser.select().where((MaterialUser.c.material == json['id']) &
                                                (MaterialUser.c.user == request['user'].id))
            result = await conn.execute(query)
            json['elected'] = result.rowcount > 0
            await result.close()
        return json
