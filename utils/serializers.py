from utils.fields import Field, Empty


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
    def __init__(self, data=Empty, **kwargs):
        self.initial_data = data
        self.validated_data = {}
        self.errors = {}
        super(Serializer, self).__init__(**kwargs)

    def is_valid(self):
        for field_name, field in self.serializer_fields.items():
            if field.read_only:
                continue

            initial_value = self.initial_data.get(field_name, Empty)
            if not field.required and initial_value is Empty:
                continue

            value = field.validate(initial_value)
            if field.validation_error is not None:
                self.errors[field_name] = field.validation_error
            else:
                self.validated_data[field_name] = value

        return not self.errors
