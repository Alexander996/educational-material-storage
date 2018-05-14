import sqlalchemy as sa

from apps.materials.models import Material
from apps.users.models import User

folder_meta = sa.MetaData()

Folder = sa.Table(
    'folder', folder_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(200), nullable=False),
    sa.Column('parent', None, sa.ForeignKey('folder.id')),
    sa.Column('user', None, sa.ForeignKey(User.c.id), nullable=False),
    sa.Column('is_open', sa.Boolean, nullable=False, server_default=sa.text('false'))
)


FolderMaterial = sa.Table(
    'foldermaterial', folder_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('material', None, sa.ForeignKey(Material.c.id), nullable=False),
    sa.Column('folder', None, sa.ForeignKey('folder.id'), nullable=False),
    sa.Column('user', None, sa.ForeignKey(User.c.id), nullable=False),
    sa.UniqueConstraint('material', 'folder', name='unique_material_folder'),
)
