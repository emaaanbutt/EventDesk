import asyncio
import logging

from app.core.logging import configure_logging
from app.db.session import new_session
from app.services.event_service import complete_due_events
from app.services.reminder_service import send_due_reminders

logger = logging.getLogger(__name__)


async def main() -> None:
    async with new_session() as db:
        completed = await complete_due_events(db)

    async with new_session() as db:
        reminded = await send_due_reminders(db)

    logger.info("Completed events: %s; reminders sent: %s", completed, reminded)


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
