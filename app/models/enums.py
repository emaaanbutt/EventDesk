from enum import StrEnum

class Role(StrEnum):
    admin = "admin"
    organizer = "orgnaizer"
    attendee = "attendee"

class EventStatus(StrEnum):
    draft = "draft"
    published = "published"
    cancelled = "cancelled"
    completed = "completed"

class BookingStatus(StrEnum):
    cancelled = "cancelled"
    confirmed = "confirmed"

class BookingType(StrEnum):
    booking_confirmed = "booking_confirmed"
    booking_cancelled = "booking_cancelled"
    new_review = "new_review"
    review_reply = "review_reply"
    review_mention = "review_mention"
    event_reminder = "event_reminder"


class WaitlistEntryStatus(StrEnum):
     waiting = "waiting"
     offered = "offered"
     converted = "converted"
     cancelled = "cancelled"
     expired = "expired"


class EventFrequency(StrEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


     
