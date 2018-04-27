class Empty(object):
    pass


class Field(object):
    expected_types = None
    error_messages = {
        'bad_value': 'Bad value "{value}" for {cls}. Value must be a {types} object',
        'required': 'This field is required'
    }

    def __init__(self, required=None, allow_null=False,
                 read_only=False, write_only=False, default=Empty):

        if required is None:
            required = default is Empty and not read_only and not allow_null

        assert not (read_only and write_only), 'Read_only and write_only'
        assert not (read_only and required), 'Read_only and required'
        assert not (required and default is not Empty), 'Required and default is not empty'

        self.required = required
        self.allow_null = allow_null
        self.read_only = read_only
        self.write_only = write_only
        self.default = default

        self.validation_error = None

    def __repr__(self):
        return 'Field(required={self.required}, allow_null={self.allow_null}, ' \
               'read_only={self.read_only}, write_only={self.write_only}, ' \
               'default={self.default})'.format(self=self)

    def validate(self, value):
        validated, value = self.validate_empty_value(value)
        if not validated:
            return value
        elif not isinstance(value, self.expected_types):
            self.set_error('bad_value', value=value, cls=self.__class__, types=self.expected_types)
        else:
            self.validation_error = None
        return value

    def validate_empty_value(self, value):
        if self.required:
            if value is Empty:
                self.set_error('required')
                return False, value
            else:
                return True, value
        else:
            if value is not Empty:
                return True, value
            elif self.default is not Empty:
                return True, self.default
            elif self.allow_null:
                return True, None

    def set_error(self, key, **kwargs):
        msg = self.error_messages[key]
        self.validation_error = msg.format(**kwargs)


class CharField(Field):
    expected_types = str


class IntegerField(Field):
    expected_types = int


class BooleanField(Field):
    expected_types = bool
