"""add attendance model

Revision ID: add_attendance_model
Revises: add_student_subject
Create Date: 2026-04-06 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'add_attendance_model'
down_revision: str = 'add_student_subject'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create attendance table
    op.create_table('attendance',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('subject', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('attendance_date', sa.Date(), nullable=False),
    sa.Column('status', sa.Enum('present', 'absent', 'late', 'excused', name='attendancestatus'), nullable=False),
    sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop attendance table
    op.drop_table('attendance')