import sqlalchemy as sa

from apps.users.models import User

material_meta = sa.MetaData()

Material = sa.Table(
    'material', material_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('auto_date', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('owner', None, sa.ForeignKey(User.c.id), nullable=False),
    sa.Column('name', sa.String(200), nullable=False),
    sa.Column('author', sa.String(200), nullable=False),
    sa.Column('file', sa.String(200), nullable=False),
    sa.Column('deleted', sa.Boolean, nullable=False, server_default=sa.text('false'))
)
