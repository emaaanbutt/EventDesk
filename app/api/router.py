from fastapi import APIRouter

from app.api.routes.audit_logs import router as audit_logs_router
from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.api.routes.categories import router as categories_router
from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.review_replies import router as review_replies_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.tags import router as tags_router
from app.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(audit_logs_router)
api_router.include_router(auth_router)
api_router.include_router(bookings_router)
api_router.include_router(categories_router)
api_router.include_router(events_router)
api_router.include_router(health_router)
api_router.include_router(notifications_router)
api_router.include_router(review_replies_router)
api_router.include_router(reviews_router)
api_router.include_router(tags_router)
api_router.include_router(users_router)
