"""Allow a new review after the previous one is soft-deleted.

Revision ID: c77f103ab690
Revises: 406c8ba94e31
"""

from alembic import op
import sqlalchemy as sa


revision = "c77f103ab690"
down_revision = "406c8ba94e31"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_active_review_author_event",
        "reviews",
        ["author_id", "event_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.drop_constraint("uq_event_author", "reviews", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("uq_event_author", "reviews", ["author_id", "event_id"])
    op.drop_index("uq_active_review_author_event", table_name="reviews")
