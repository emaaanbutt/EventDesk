from enum import StrEnum

from app.models.enums import PermissionScope, Role


class Action(StrEnum):
    profile_update = "profile.update"
    password_change = "password.change"
    users_list = "users.list"
    users_role_change = "users.role.change"
    users_active_change = "users.active.change"
    users_delete = "users.delete"
    events_create = "events.create"
    events_edit = "events.edit"
    events_cancel = "events.cancel"
    events_view_published = "events.view_published"
    bookings_create = "bookings.create"
    bookings_cancel = "bookings.cancel"
    reviews_create = "reviews.create"
    reviews_reply = "reviews.reply"
    reviews_edit = "reviews.edit"
    reviews_delete = "reviews.delete"
    notifications_view = "notifications.view"
    audit_logs_view = "audit_logs.view"

ROLE_PERMISSIONS: dict[Role, dict[Action, PermissionScope]] = {
    Role.admin: {
        Action.profile_update: PermissionScope.self,
        Action.password_change: PermissionScope.self,
        Action.users_list: PermissionScope.global_,
        Action.users_role_change: PermissionScope.any,
        Action.users_active_change: PermissionScope.any,
        Action.users_delete: PermissionScope.any,
        Action.events_create: PermissionScope.global_,
        Action.events_edit: PermissionScope.any,
        Action.events_cancel: PermissionScope.any,
        Action.events_view_published: PermissionScope.global_,
        Action.bookings_create: PermissionScope.global_,
        Action.bookings_cancel: PermissionScope.any,
        Action.reviews_create: PermissionScope.global_,
        Action.reviews_reply: PermissionScope.any,
        Action.reviews_edit: PermissionScope.any,
        Action.reviews_delete: PermissionScope.any,
        Action.notifications_view: PermissionScope.self,
        Action.audit_logs_view: PermissionScope.global_,
    },
    Role.organizer: {
        Action.profile_update: PermissionScope.self,
        Action.password_change: PermissionScope.self,
        Action.events_create: PermissionScope.global_,
        Action.events_edit: PermissionScope.own_event,
        Action.events_cancel: PermissionScope.own_event,
        Action.events_view_published: PermissionScope.global_,
        Action.bookings_create: PermissionScope.global_,
        Action.bookings_cancel: PermissionScope.own,
        Action.reviews_create: PermissionScope.global_,
        Action.reviews_reply: PermissionScope.own_event,
        Action.reviews_edit: PermissionScope.own,
        Action.reviews_delete: PermissionScope.own,
        Action.notifications_view: PermissionScope.self,
    },
    Role.attendee: {
        Action.profile_update: PermissionScope.self,
        Action.password_change: PermissionScope.self,
        Action.events_view_published: PermissionScope.global_,
        Action.bookings_create: PermissionScope.global_,
        Action.bookings_cancel: PermissionScope.own,
        Action.reviews_create: PermissionScope.global_,
        Action.reviews_edit: PermissionScope.own,
        Action.reviews_delete: PermissionScope.own,
        Action.notifications_view: PermissionScope.self,
    },
}
