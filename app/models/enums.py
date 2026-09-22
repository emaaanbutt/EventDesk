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

class BookingStaus(StrEnum):
    cancelled = "cancelled"
    confirmed = "confirmed"

