import sqlalchemy as sa

from apps.users.models import User

token_meta = sa.MetaData()

Token = sa.Table(
    'token', token_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('key', sa.String(50), nullable=False, unique=True),
    sa.Column('user', None, sa.ForeignKey(User.c.id), nullable=False)
)
