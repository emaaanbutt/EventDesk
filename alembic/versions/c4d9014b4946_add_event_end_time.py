"""add event end time

Revision ID: c4d9014b4946
Revises: 406c8ba94e31
Create Date: 2026-09-25 20:15:24.261126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d9014b4946'
down_revision: Union[str, Sequence[str], None] = '406c8ba94e31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("events", sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False))
    op.create_check_constraint(
        "ck_events_end_after_start", "events", "ends_at > starts_at"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_events_end_after_start", "events", type_="check")
    op.drop_column("events", "ends_at")
