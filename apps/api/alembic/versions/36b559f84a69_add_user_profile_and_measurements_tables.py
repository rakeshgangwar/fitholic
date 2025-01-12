"""add_user_profile_and_measurements_tables

Revision ID: 36b559f84a69
Revises: 506fc9977d88
Create Date: 2025-01-12 10:55:34.977054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36b559f84a69'
down_revision: Union[str, None] = '506fc9977d88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('height', sa.Float(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('gender', sa.String(), nullable=True),
    sa.Column('fitness_goals', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('preferred_workout_duration', sa.Integer(), nullable=True),
    sa.Column('preferred_workout_days', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('available_equipment', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('theme', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('units', sa.String(), nullable=True),
    sa.Column('notification_settings', sa.JSON(), nullable=True),
    sa.Column('privacy_settings', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('user_measurements',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('body_fat', sa.Float(), nullable=True),
    sa.Column('measurements', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default='now()', nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default='now()', nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], ['user_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_measurements')
    op.drop_table('user_profiles')
    # ### end Alembic commands ###
