"""Seed permission codes and role scopes.

Revision ID: a74e6b27c901
Revises: e82ee27ac6c8
"""

from uuid import NAMESPACE_URL, uuid5

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "a74e6b27c901"
down_revision = "e82ee27ac6c8"
branch_labels = None
depends_on = None


PERMISSIONS = (
    ("profile.update", "Update own profile"),
    ("password.change", "Change own password"),
    ("users.list", "View users"),
    ("users.role.change", "Change user roles"),
    ("users.active.change", "Activate or deactivate users"),
    ("users.delete", "Soft delete users"),
    ("events.create", "Create events"),
    ("events.edit", "Edit events"),
    ("events.publish", "Publish events"),
    ("events.complete", "Complete events"),
    ("events.cancel", "Cancel events"),
    ("events.view_published", "View published events"),
    ("events.view_own", "View own events"),
    ("categories.create", "Create categories"),
    ("tags.create", "Create tags"),
    ("bookings.create", "Create bookings"),
    ("bookings.view", "View bookings"),
    ("bookings.cancel", "Cancel bookings"),
    ("reviews.create", "Create reviews"),
    ("reviews.reply", "Reply to reviews"),
    ("reviews.edit", "Edit reviews"),
    ("reviews.delete", "Delete reviews"),
    ("notifications.view", "View notifications"),
    ("notifications.edit", "Mark notifications read or unread"),
    ("audit_logs.view", "View audit logs"),
)

GRANTS = {
    "admin": {
        "profile.update": "self",
        "password.change": "self",
        "users.list": "global",
        "users.role.change": "any",
        "users.active.change": "any",
        "users.delete": "any",
        "events.create": "global",
        "events.edit": "any",
        "events.publish": "any",
        "events.complete": "any",
        "events.cancel": "any",
        "events.view_published": "global",
        "events.view_own": "global",
        "categories.create": "global",
        "tags.create": "global",
        "bookings.create": "global",
        "bookings.view": "any",
        "bookings.cancel": "any",
        "reviews.create": "global",
        "reviews.reply": "any",
        "reviews.edit": "any",
        "reviews.delete": "any",
        "notifications.view": "self",
        "notifications.edit": "self",
        "audit_logs.view": "global",
    },
    "organizer": {
        "profile.update": "self",
        "password.change": "self",
        "events.create": "global",
        "events.edit": "own_event",
        "events.publish": "own_event",
        "events.complete": "own_event",
        "events.cancel": "own_event",
        "events.view_published": "global",
        "events.view_own": "global",
        "bookings.create": "global",
        "bookings.view": "own",
        "bookings.cancel": "own",
        "reviews.create": "global",
        "reviews.reply": "own_event",
        "reviews.edit": "own",
        "reviews.delete": "own",
        "notifications.view": "self",
        "notifications.edit": "self",
    },
    "attendee": {
        "profile.update": "self",
        "password.change": "self",
        "events.view_published": "global",
        "bookings.create": "global",
        "bookings.view": "own",
        "bookings.cancel": "own",
        "reviews.create": "global",
        "reviews.edit": "own",
        "reviews.delete": "own",
        "notifications.view": "self",
        "notifications.edit": "self",
    },
}

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
