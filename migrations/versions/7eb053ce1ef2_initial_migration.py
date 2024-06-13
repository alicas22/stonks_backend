"""Initial migration

Revision ID: 7eb053ce1ef2
Revises: 
Create Date: 2024-06-12 13:00:05.889631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7eb053ce1ef2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profile',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('fullName', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('createdAt', sa.DateTime(), nullable=True),
    sa.Column('updatedAt', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('channel',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('host_id', sa.String(length=36), nullable=False),
    sa.Column('createdAt', sa.DateTime(), nullable=True),
    sa.Column('updatedAt', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['host_id'], ['profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fcm_token',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('token', sa.String(length=255), nullable=False),
    sa.Column('profile_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_status',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('profile_id', sa.String(length=36), nullable=False),
    sa.Column('is_online', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('profile_id', sa.String(length=36), nullable=False),
    sa.Column('channel_id', sa.String(length=36), nullable=True),
    sa.ForeignKeyConstraint(['channel_id'], ['channel.id'], ),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('webhook',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('url', sa.String(length=255), nullable=False),
    sa.Column('channel_id', sa.String(length=36), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channel.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('webhook')
    op.drop_table('role')
    op.drop_table('user_status')
    op.drop_table('fcm_token')
    op.drop_table('channel')
    op.drop_table('profile')
    # ### end Alembic commands ###