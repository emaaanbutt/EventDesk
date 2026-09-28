from enum import StrEnum


class Role(StrEnum):
    admin = "admin"
    organizer = "organizer"
    attendee = "attendee"


class EventStatus(StrEnum):
    draft = "draft"
    published = "published"
    cancelled = "cancelled"
    completed = "completed"


class BookingStatus(StrEnum):
    cancelled = "cancelled"
    confirmed = "confirmed"


class NotificationCategory(StrEnum):
    booking = "booking"
    event = "event"
    review = "review"


class PermissionScope(StrEnum):
    global_ = "global"
    self = "self"
    own = "own"
    own_event = "own_event"
    any = "any"
