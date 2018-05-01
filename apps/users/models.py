import sqlalchemy as sa

user_meta = sa.MetaData()

User = sa.Table(
    'user', user_meta,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(200), nullable=False, unique=True),
    sa.Column('password', sa.String(200), nullable=False),
    sa.Column('email', sa.String(200), nullable=False),
    sa.Column('first_name', sa.String(200)),
    sa.Column('last_name', sa.String(200)),
    sa.Column('role', sa.Integer, nullable=False),
    sa.Column('blocked', sa.Boolean, nullable=False, server_default=sa.text('false'))
)
