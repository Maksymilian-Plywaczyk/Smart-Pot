"""First migration

Revision ID: 69d724eb9c27
Revises: 
Create Date: 2023-09-26 11:50:21.407630

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '69d724eb9c27'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'blacklisttoken',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('invalidated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_blacklisttoken_id'), 'blacklisttoken', ['id'], unique=False
    )
    op.create_index(
        op.f('ix_blacklisttoken_token'), 'blacklisttoken', ['token'], unique=True
    )
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_full_name'), 'user', ['full_name'], unique=False)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_table(
        'device',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('device_token', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_token'),
    )
    op.create_index(op.f('ix_device_id'), 'device', ['id'], unique=False)
    op.create_index(op.f('ix_device_name'), 'device', ['name'], unique=True)
    op.create_table(
        'plant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('imgsrc', sa.String(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('lux', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('device_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ['device_id'],
            ['device.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_plant_id'), 'plant', ['id'], unique=False)
    op.create_index(op.f('ix_plant_name'), 'plant', ['name'], unique=False)
    op.create_table(
        'plant_hist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('lux', sa.Float(), nullable=False),
        sa.Column('humidity', sa.Float(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=True),
        sa.Column('plant_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['plant_id'],
            ['plant.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_plant_hist_id'), 'plant_hist', ['id'], unique=False)
    op.create_table(
        'sensorthreshold',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sensor_name', sa.String(), nullable=False),
        sa.Column('min_value', sa.Integer(), nullable=False),
        sa.Column('max_value', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('plant_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['plant_id'],
            ['plant.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_sensorthreshold_id'), 'sensorthreshold', ['id'], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sensorthreshold_id'), table_name='sensorthreshold')
    op.drop_table('sensorthreshold')
    op.drop_index(op.f('ix_plant_hist_id'), table_name='plant_hist')
    op.drop_table('plant_hist')
    op.drop_index(op.f('ix_plant_name'), table_name='plant')
    op.drop_index(op.f('ix_plant_id'), table_name='plant')
    op.drop_table('plant')
    op.drop_index(op.f('ix_device_name'), table_name='device')
    op.drop_index(op.f('ix_device_id'), table_name='device')
    op.drop_table('device')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_full_name'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_blacklisttoken_token'), table_name='blacklisttoken')
    op.drop_index(op.f('ix_blacklisttoken_id'), table_name='blacklisttoken')
    op.drop_table('blacklisttoken')
    # ### end Alembic commands ###