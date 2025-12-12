from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class ClerkWebhookEvent(BaseModel):
    """
    Clerk webhook event envelope.
    https://clerk.com/docs/guides/development/webhooks/overview
    """
    object: Literal["event"] = "event"
    type: str = Field(..., description="Event type, e.g. user.created")
    data: Dict[str, Any] = Field(..., description="Event payload")
    timestamp: int = Field(..., description="Event timestamp in milliseconds")
    instance_id: str = Field(..., description="Clerk instance id")

    # Sometimes present depending on tooling / wrappers; keep optional.
    id: Optional[str] = None

    class Config:
        frozen = True
