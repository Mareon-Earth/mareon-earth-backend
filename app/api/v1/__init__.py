from fastapi import APIRouter

from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.auth_test import router as auth_test_router
from app.api.v1.routers.clerk_webhooks import router as clerk_webhooks_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_test_router)
api_router.include_router(clerk_webhooks_router)
