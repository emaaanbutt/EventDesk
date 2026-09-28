import asyncio

from app.db.session import AsyncSessionLocal
from app.services.event_service import complete_due_events
from app.services.reminder_service import send_due_reminders


async def main() -> None:
    async with AsyncSessionLocal() as db:
        completed = await complete_due_events(db)

    async with AsyncSessionLocal() as db:
        reminded = await send_due_reminders(db)

    print(f"Completed events: {completed}; reminders sent: {reminded}")


if __name__ == "__main__":
    asyncio.run(main())
