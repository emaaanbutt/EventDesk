"""Remove the unused permission for publicly visible events.

Revision ID: b19c8f6e2a31
Revises: a74e6b27c901
"""

from uuid import NAMESPACE_URL, uuid5

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "b19c8f6e2a31"
down_revision = "a74e6b27c901"
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


def upgrade() -> None:
    op.get_bind().execute(
        sa.delete(permissions).where(permissions.c.code == "events.view_published")
    )


def downgrade() -> None:
    code = "events.view_published"
    permission_id = uuid5(NAMESPACE_URL, f"eventdesk.permission.{code}")
    op.bulk_insert(
        permissions,
        [{"id": permission_id, "code": code, "description": "View published events"}],
    )
    op.bulk_insert(
        role_permissions,
        [
            {
                "id": uuid5(NAMESPACE_URL, f"eventdesk.role_permission.{role}.{code}"),
                "role": role,
                "permission_id": permission_id,
                "scope": "global",
            }
            for role in ("admin", "organizer", "attendee")
        ],
    )
