"""Add delete permissions and repair bookings of cancelled events.

Revision ID: 8f31d9a2c6be
Revises: e99cac845e89
"""

from uuid import NAMESPACE_URL, uuid5

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "8f31d9a2c6be"
down_revision = "e99cac845e89"
branch_labels = None
depends_on = None


permissions = sa.table(
    "permissions",
    sa.column("id", sa.UUID(as_uuid=True)),
    sa.column("code", sa.String()),
    sa.column("description", sa.String()),
)
role_permissions = sa.table(
    "role_permissions",
    sa.column("id", sa.UUID(as_uuid=True)),
    sa.column("role", postgresql.ENUM("admin", "organizer", "attendee", name="role", create_type=False)),
    sa.column("permission_id", sa.UUID(as_uuid=True)),
    sa.column(
        "scope",
        postgresql.ENUM("global", "self", "own", "own_event", "any", name="permission_scope", create_type=False),
    ),
)

PERMISSIONS = (
    ("events.delete", "Soft delete events"),
    ("events.view_all", "View all events"),
    ("bookings.delete", "Soft delete bookings"),
)
GRANTS = {
    "admin": {"events.delete": "any", "events.view_all": "global", "bookings.delete": "any"},
    "organizer": {"events.delete": "own_event", "bookings.delete": "own"},
    "attendee": {"bookings.delete": "own"},
}


def permission_id(code: str):
    return uuid5(NAMESPACE_URL, f"eventdesk.permission.{code}")


def grant_id(role: str, code: str):
    return uuid5(NAMESPACE_URL, f"eventdesk.role_permission.{role}.{code}")


def upgrade() -> None:
    op.bulk_insert(
        permissions,
        [
            {"id": permission_id(code), "code": code, "description": description}
            for code, description in PERMISSIONS
        ],
    )
    op.bulk_insert(
        role_permissions,
        [
            {
                "id": grant_id(role, code),
                "role": role,
                "permission_id": permission_id(code),
                "scope": scope,
            }
            for role, grants in GRANTS.items()
            for code, scope in grants.items()
        ],
    )
    op.execute(sa.text("""
        UPDATE bookings AS booking
        SET status = 'cancelled',
            cancelled_at = COALESCE(booking.cancelled_at, event.updated_at),
            updated_at = now()
        FROM events AS event
        WHERE booking.event_id = event.id
          AND booking.status = 'confirmed'
          AND booking.deleted_at IS NULL
          AND event.status = 'cancelled'
    """))


def downgrade() -> None:
    op.get_bind().execute(
        sa.delete(role_permissions).where(
            role_permissions.c.id.in_(
                [grant_id(role, code) for role, grants in GRANTS.items() for code in grants]
            )
        )
    )
    op.get_bind().execute(
        sa.delete(permissions).where(
            permissions.c.id.in_([permission_id(code) for code, _ in PERMISSIONS])
        )
    )
