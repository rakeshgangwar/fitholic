"""add_server_default_to_user_timestamps

Revision ID: 213afeab79bf
Revises: 36b559f84a69
Create Date: 2024-01-12 12:43:02.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '213afeab79bf'
down_revision: Union[str, None] = '36b559f84a69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set server_default for created_at and updated_at
    op.alter_column('users', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('users', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=sa.text('now()'),
               existing_nullable=True)


def downgrade() -> None:
    # Remove server_default
    op.alter_column('users', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=None,
               existing_nullable=True)
    op.alter_column('users', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               server_default=None,
               existing_nullable=True)
