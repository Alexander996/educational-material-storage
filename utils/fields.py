empty = object()


class Field(object):
    types = ()
    error_messages = {
        'bad_value': 'Bad value "{value}" for {cls}. Value must be a {types} objects',
        'required': 'This field is required'
    }

    def __init__(self, required=None, allow_null=False,
                 read_only=False, write_only=False, default=empty):

        if required is None:
            required = default is empty and not read_only and not allow_null

        assert not (read_only and write_only), 'Read_only and write_only'
        assert not (read_only and required), 'Read_only and required'
        assert not (required and default is not empty), 'Required and default is not empty'

        self.required = required
        self.allow_null = allow_null
        self.read_only = read_only
        self.write_only = write_only
        self.default = default

        self.validation_error = None

    def __repr__(self):
        return 'Field(required={required}, allow_null={allow_null}, ' \
               'read_only={read_only}, write_only={write_only}, ' \
               'default={default})'.format(required=self.required,
                                           allow_null=self.allow_null,
                                           read_only=self.read_only,
                                           write_only=self.write_only,
                                           default=self.default)

    def validate(self, value):
        is_empty = self.validate_empty_value(value)
        if is_empty:
            return
        elif not isinstance(value, self.types):
            self.set_error('bad_value', value=value, cls=self.__class__, types=self.types)
        else:
            self.validation_error = None

    def validate_empty_value(self, value):
        if self.required and value is empty:
            self.set_error('required')
            return True
        elif self.read_only:
            return True
        return False

    def set_error(self, key, **kwargs):
        msg = self.error_messages[key]
        self.validation_error = msg.format(**kwargs)


class CharField(Field):
    types = (str,)


class IntegerField(Field):
    types = (int,)
