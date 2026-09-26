from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.audit_logs import router as audit_logs_router
from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.api.routes.categories import router as categories_router
from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.realtime import router as realtime_router
from app.api.routes.review_replies import router as review_replies_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.tags import router as tags_router
from app.api.routes.users import router as users_router

app = FastAPI(title="EventDesk", version="1.0.0")
app.include_router(audit_logs_router)
app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(categories_router)
app.include_router(events_router)
app.include_router(health_router)
app.include_router(notifications_router)
app.include_router(realtime_router)
app.include_router(review_replies_router)
app.include_router(reviews_router)
app.include_router(tags_router)
app.include_router(users_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "EventDesk API is running"}
