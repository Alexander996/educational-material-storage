import sqlalchemy as sa

category_meta = sa.MetaData()

Category = sa.Table(
    'category', category_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(200), nullable=False, unique=True),
    sa.Column('deleted', sa.Boolean, nullable=False, default=False)
)
