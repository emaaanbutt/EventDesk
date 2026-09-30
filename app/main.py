from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.api.routes.realtime import router as realtime_router
from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.core.logging import configure_logging
from app.db.session import get_engine

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    get_settings()
    if not (frontend_dist / "index.html").is_file():
        raise RuntimeError("Frontend build missing. Run `pnpm build` in frontend/ first.")
    engine = get_engine()
    try:
        yield
    finally:
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="EventDesk", version="1.0.0", lifespan=lifespan)

    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    app.include_router(api_router, prefix="/api")
    app.include_router(realtime_router)
    app.frontend("/", directory=frontend_dist, fallback="index.html", check_dir=False)
    return app


app = create_app()
