from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.exceptions import register_exception_handlers
from app.core.seed import seed_database, seed_demo_data

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Initialising database…")
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
        seed_demo_data(db)
    finally:
        db.close()
    logger.info("Startup complete.")

    yield

    # Shutdown (nothing to tear down for SQLite)
    logger.info("Shutdown complete.")


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(application)

    # Health check
    @application.get("/health", tags=["meta"])
    def health_check() -> dict:
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "active_standard": settings.ACTIVE_STANDARD,
        }

    # API v1 router
    from app.api.v1.router import api_router
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Mount frontend SPA if built
    import os
    frontend_dist = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../frontend/dist")
    )
    if os.path.exists(frontend_dist):
        from fastapi.staticfiles import StaticFiles
        application.mount(
            "/",
            StaticFiles(directory=frontend_dist, html=True),
            name="frontend",
        )

    return application


app = create_app()
