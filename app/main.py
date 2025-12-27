from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers
from app.infrastructure.db import database_lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Ensures database connections are properly closed
    - Cleans up Cloud SQL Connector resources
    - Can be extended for other resource management
    """
    # Startup
    async with database_lifespan():
        yield


def create_app() -> FastAPI:
    # Ensure env is loaded + validated at startup
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,  # Added lifespan manager
    )

    # Routers
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Global error handlers
    register_error_handlers(app)

    return app


app = create_app()
