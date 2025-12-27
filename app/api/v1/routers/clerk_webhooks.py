from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession # Required for db dependency

from app.core.config import Settings, get_settings
from app.core.auth.webhooks import verify_clerk_webhook
from app.core.auth.webhooks.handlers import dispatch_webhook_event
from app.infrastructure.db import get_db_session

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
):
    """
    Clerk webhook endpoint.
    Verifies signature and dispatches events to appropriate handlers.
    """
    raw_body = await request.body()
    event = verify_clerk_webhook(
        raw_body=raw_body,
        headers=dict(request.headers),
        secret=settings.clerk_webhook_secret,
    )

    # Dispatch to handler
    await dispatch_webhook_event(event.type, event.data, db)

    return {"ok": True, "type": event.type}
