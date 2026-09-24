from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router

app = FastAPI(title="EventDesk", version="1.0.0")
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(users_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "EventDesk API is running"}
