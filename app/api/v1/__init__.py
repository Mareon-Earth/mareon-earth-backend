"""API v1 router registry."""

from fastapi import APIRouter

from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.clerk_webhooks import router as clerk_webhooks_router
from app.api.v1.routers.documents import router as documents_router
from app.api.v1.routers.vessels import router as vessels_router
from app.api.v1.routers.pubsub_webhooks import router as pubsub_webhooks_router
api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(clerk_webhooks_router)
api_router.include_router(documents_router)
api_router.include_router(vessels_router)
api_router.include_router(pubsub_webhooks_router)

__all__ = ["api_router"]
