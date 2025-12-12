from fastapi import APIRouter, Depends, Request

from app.core.config import Settings, get_settings
from app.core.auth.webhooks import verify_clerk_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/clerk")
async def clerk_webhook(request: Request, settings: Settings = Depends(get_settings)):
    raw_body = await request.body()
    event = verify_clerk_webhook(
        raw_body=raw_body,
        headers=dict(request.headers),
        secret=settings.clerk_webhook_secret,
    )

    # For now: just acknowledge + basic visibility
    # Later: dispatch by event.type to handlers
    return {"ok": True, "type": event.type}
