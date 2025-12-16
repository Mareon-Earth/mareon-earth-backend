from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers


def create_app() -> FastAPI:
    # Ensure env is loaded + validated at startup
    settings = get_settings()

    app = FastAPI(
        title="Mareon Backend",
        version="0.1.0",
    )

    # Routers
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Global error handlers
    register_error_handlers(app)

    return app


app = create_app()
