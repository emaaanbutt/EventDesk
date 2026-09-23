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


class NotificationType(StrEnum):
    booking_confirmed = "booking_confirmed"
    booking_cancelled = "booking_cancelled"
    new_review = "new_review"
    review_reply = "review_reply"
    review_mention = "review_mention"
    event_reminder = "event_reminder"


class PermissionScope(StrEnum):
    global_ = "global"
    self = "self"
    own = "own"
    own_event = "own_event"
    any = "any"
