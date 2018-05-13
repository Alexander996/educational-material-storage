from apps.folders.models import Folder, FolderMaterial
from apps.materials.models import Material
from apps.materials.serializers import MaterialSerializer
from utils import serializers


class FolderMaterialSerializer(serializers.Serializer):
    material = serializers.ForeignKeyField(model=Material)

    async def to_json(self, result):
        json = await super(FolderMaterialSerializer, self).to_json(result)
        async with self.context['request'].app['db'].acquire() as conn:
            query = Material.select().where(Material.c.id == json['material'])
            result = await conn.execute(query)
            serializer = MaterialSerializer(context=self.context)
            material = await serializer.to_json(result)
            return material


class FolderSerializer(serializers.ModelSerializer):
    parent = serializers.ForeignKeyField(model=Folder, allow_null=True)

    class Meta:
        model = Folder
        exclude = ('user',)

    async def is_valid(self, method, partial=False):
        await super(FolderSerializer, self).is_valid(method, partial=partial)
        self.validated_data['user'] = self.context['request']['user'].id

        if method == 'create':
            parent = self.validated_data['parent']
            self.validated_data['parent'] = parent.id if parent is not None else None
        else:
            self.validated_data.pop('parent', None)


class FolderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = '__all__'
        read_only_fields = ('user',)

    async def to_json(self, result):
        json = await super(FolderDetailSerializer, self).to_json(result)
        request = self.context['request']

        async with request.app['db'].acquire() as conn:
            query = Folder.select().where(Folder.c.parent == json['id'])
            result = await conn.execute(query)
            folder_serializer = FolderSerializer(many=True, context=self.context)
            folders = await folder_serializer.to_json(result)
            if json['user'] != request['user'].id:
                for folder in folders:
                    if not folder['is_open']:
                        folders.remove(folder)

            json['folders'] = folders

            query = FolderMaterial.select().where(FolderMaterial.c.folder == json['id'])
            result = await conn.execute(query)
            serializer = FolderMaterialSerializer(many=True, context=self.context)
            materials = await serializer.to_json(result)
            if json['user'] != request['user'].id:
                for material in materials:
                    if not material['is_open']:
                        materials.remove(material)

            json['materials'] = materials
            return json
