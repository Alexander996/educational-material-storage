from utils.fields import Field, empty


class SerializerMeta(type):
    def __new__(mcs, name, bases, attrs):
        fields = [(field_name, attrs.pop(field_name))
                  for field_name, obj in list(attrs.items())
                  if isinstance(obj, Field)]

        for base in reversed(bases):
            if hasattr(base, 'serializer_fields'):
                fields += [(field_name, obj) for field_name, obj
                           in base.serializer_fields.items()
                           if field_name not in attrs]

        attrs['serializer_fields'] = dict(fields)
        return super(SerializerMeta, mcs).__new__(mcs, name, bases, attrs)


class Serializer(Field, metaclass=SerializerMeta):
    def __init__(self, data=empty, **kwargs):
        self.initial_data = data
        self.validated_data = None
        self.errors = {}
        super(Serializer, self).__init__(**kwargs)

    def is_valid(self):
        data = {}

        for field, value in self.initial_data.items():
            if field in self.fields.keys() and field != 'id':
                data[field] = value

        for field_name, field in self.fields.items():
            field.validate(data.get(field_name, empty))
            if field.validation_error is not None:
                self.errors[field_name] = field.validation_error

        self.validated_data = data
        return not self.errors

    @property
    def fields(self):
        return self.serializer_fields
