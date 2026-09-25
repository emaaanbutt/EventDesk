"""Simplify notification types to booking, event, and review.

Revision ID: f8c3be69ad12
Revises: 4182a4741d50
"""

from alembic import op


revision = "f8c3be69ad12"
down_revision = "4182a4741d50"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE notification_type RENAME TO notification_type_old")
    op.execute("CREATE TYPE notification_type AS ENUM ('booking', 'event', 'review')")
    op.execute(
        """
        ALTER TABLE notifications
        ALTER COLUMN type TYPE notification_type
        USING (
            CASE
                WHEN type::text IN ('booking_confirmed', 'booking_cancelled') THEN 'booking'
                WHEN type::text IN ('event_cancelled', 'event_reminder') THEN 'event'
                WHEN type::text IN ('new_review', 'review_reply') THEN 'review'
            END
        )::notification_type
        """
    )
    op.execute("DROP TYPE notification_type_old")


def downgrade() -> None:
    raise NotImplementedError(
        "The original detailed notification types cannot be recovered after conversion"
    )
