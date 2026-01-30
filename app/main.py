from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.error_handlers import register_error_handlers
from app.infrastructure.db import database_lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database_lifespan():
        yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    # ✅ CORS (must be added BEFORE routers)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://mareon.app",
            "https://accounts.mareon.app",  # helps during auth flows
        ],
        allow_credentials=False,  # set True ONLY if you're using cookies
        allow_methods=["*"],      # includes OPTIONS preflight
        allow_headers=["*"],      # includes Authorization, Content-Type, etc.
    )

    # Routers
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Global error handlers
    register_error_handlers(app)

    return app


app = create_app()
