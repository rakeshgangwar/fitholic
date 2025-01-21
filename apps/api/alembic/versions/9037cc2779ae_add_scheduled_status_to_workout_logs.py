"""add_scheduled_status_to_workout_logs

Revision ID: 9037cc2779ae
Revises: c6b6ccc87c49
Create Date: 2025-01-21 15:16:51.329207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9037cc2779ae'
down_revision: Union[str, None] = 'c6b6ccc87c49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make start_time nullable
    op.alter_column('workout_logs', 'start_time',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=True)
    
    # Update existing records to have status based on end_time and dates
    op.execute("""
        UPDATE workout_logs 
        SET status = CASE 
            WHEN end_time IS NOT NULL THEN 'completed'
            WHEN date > CURRENT_DATE THEN 'scheduled'
            WHEN date = CURRENT_DATE AND start_time > CURRENT_TIMESTAMP THEN 'scheduled'
            ELSE 'ongoing'
        END
    """)
    
    # Update default value for status column
    op.alter_column('workout_logs', 'status',
                    existing_type=sa.String(),
                    server_default='scheduled',
                    existing_nullable=False)


def downgrade() -> None:
    # Make start_time non-nullable again
    op.alter_column('workout_logs', 'start_time',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=False)
    
    # Revert default value for status column
    op.alter_column('workout_logs', 'status',
                    existing_type=sa.String(),
                    server_default='ongoing',
                    existing_nullable=False)
