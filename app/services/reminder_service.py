from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.integrations.brevo import send_email
from app.repositories.booking_repository import BookingRepository

logger = logging.getLogger(__name__)


async def send_due_reminders(db: AsyncSession) -> int:
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(hours=settings.REMINDER_HOURS_BEFORE)
    display_timezone = ZoneInfo(settings.REMINDER_TIMEZONE)
    bookings = await BookingRepository.get_due_reminders_for_update(now, cutoff, 50, db)
    sent_count = 0

    for booking in bookings:
        event = booking.event
        attendee = booking.attendee
        start_time = event.starts_at.astimezone(display_timezone).strftime("%d %b %Y, %I:%M %p %Z")
        html_content = (
            f"<p>Hi {escape(attendee.name)},</p>"
            f"<p>Your event <strong>{escape(event.title)}</strong> starts "
            f"on {start_time} at {escape(event.venue)}.</p>"
        )
        try:
            await send_email(
                to_email=attendee.email,
                to_name=attendee.name,
                subject="Your EventDesk event is coming up",
                html_content=html_content,
            )
        except (httpx.HTTPError, ValueError):
            logger.exception("Could not send reminder for booking %s", booking.id)
            continue

        await BookingRepository.mark_reminder_sent(booking, datetime.now(timezone.utc), db)
        sent_count += 1

    await db.commit()
    return sent_count
