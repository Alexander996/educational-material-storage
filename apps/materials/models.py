import sqlalchemy as sa

from apps.categories.models import Category
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
    sa.Column('type', sa.Integer, nullable=False),
    sa.Column('extension', sa.String(10), nullable=False),
    sa.Column('deleted', sa.Boolean, nullable=False, server_default=sa.text('false')),
    sa.Column('is_open', sa.Boolean, nullable=False, server_default=sa.text('false'))
)


Comment = sa.Table(
    'comment', material_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('auto_date', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('material', None, sa.ForeignKey('material.id'), nullable=False),
    sa.Column('text', sa.String(1000), nullable=False),
    sa.Column('user', None, sa.ForeignKey(User.c.id), nullable=False)
)


MaterialCategory = sa.Table(
    'materialcategory', material_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('material', None, sa.ForeignKey('material.id'), nullable=False),
    sa.Column('category', None, sa.ForeignKey(Category.c.id), nullable=False),
    sa.UniqueConstraint('material', 'category', name='unique_material_category')
)


MaterialUser = sa.Table(
    'materialuser', material_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('material', None, sa.ForeignKey('material.id'), nullable=False),
    sa.Column('user', None, sa.ForeignKey(User.c.id), nullable=False),
    sa.Column('quick_toolbar', sa.Boolean, nullable=False, server_default=sa.text('false')),
    sa.UniqueConstraint('material', 'user', name='unique_material_user')
)
