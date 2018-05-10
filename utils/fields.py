import re
from datetime import datetime

from aiohttp.web_request import FileField as AioFileField

from utils.db import CurrentDBConnection
from utils.hash import hash_password


class Empty(object):
    pass


class Field(object):
    expected_types = None
    error_messages = {
        'bad_value': 'Bad value "{value}" for {cls}. Value must be a {types} object',
        'required': 'This field is required'
    }

    def __init__(self, required=None, allow_null=False, model=None,
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
        self.model = model

        self.validation_error = None

    def __repr__(self):
        return 'Field(required={self.required}, allow_null={self.allow_null}, ' \
               'read_only={self.read_only}, write_only={self.write_only}, ' \
               'default={self.default})'.format(self=self)

    async def validate(self, value):
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
                return False, self.default
            elif self.allow_null:
                return False, None

    def set_error(self, key, **kwargs):
        msg = self.error_messages[key]
        self.validation_error = msg.format(**kwargs)

    async def to_representation(self, value):
        pass


class CharField(Field):
    expected_types = str

    async def to_representation(self, value):
        return str(value) if value is not None else None


class IntegerField(Field):
    expected_types = int

    async def validate(self, value):
        try:
            value = int(value)
        except ValueError:
            pass
        except TypeError:
            pass

        return await super(IntegerField, self).validate(value)

    async def to_representation(self, value):
        return int(value) if value is not None else None


class BooleanField(Field):
    expected_types = bool
    FALSE_VALUES = (False, 'false', 0, '0')
    TRUE_VALUES = (True, 'true', 1, '1')

    async def validate(self, value):
        if value in self.FALSE_VALUES:
            value = False
        elif value in self.TRUE_VALUES:
            value = True

        return await super(BooleanField, self).validate(value)

    async def to_representation(self, value):
        return bool(value) if value is not None else None


class EmailField(Field):
    expected_types = str

    async def validate(self, value):
        value = await super(EmailField, self).validate(value)
        if self.validation_error is not None:
            return value

        pattern = re.compile('^[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}$')
        is_valid = pattern.match(value)
        if not is_valid:
            self.validation_error = 'Email not valid'
        return value

    async def to_representation(self, value):
        return str(value) if value is not None else None


class PasswordField(Field):
    expected_types = str

    async def validate(self, value):
        value = await super(PasswordField, self).validate(value)
        if self.validation_error is not None:
            return value

        password = hash_password(value)
        return password

    async def to_representation(self, value):
        return str(value) if value is not None else None


class ForeignKeyField(Field):
    expected_types = int

    async def validate(self, value):
        value = await super(ForeignKeyField, self).validate(value)
        if self.validation_error is not None:
            return value

        model = self.model
        db = CurrentDBConnection.get_db_connection()
        async with db.acquire() as conn:
            query = model.select().where(model.c.id == value)
            result = await conn.execute(query)
            if result.rowcount == 0:
                self.validation_error = 'pk {} not found'.format(value)
                return value

            obj = await result.fetchone()

        return obj

    async def to_representation(self, value):
        return int(value) if value is not None else None


class DateTimeField(Field):
    expected_types = datetime

    async def to_representation(self, value):
        return value.isoformat() if value is not None else None


class FileField(Field):
    expected_types = (AioFileField, str)

    def __init__(self, upload_to=None, **kwargs):
        self.upload_to = upload_to
        super(FileField, self).__init__(**kwargs)

    async def to_representation(self, value):
        return str(value) if value is not None else None
