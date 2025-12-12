import json
from typing import Mapping

from svix.webhooks import Webhook

from app.core.auth.webhooks.types import ClerkWebhookEvent
from app.core.auth.exceptions import WebhookSignatureError


def _normalize_headers(headers: Mapping[str, str]) -> dict[str, str]:
    # FastAPI headers are case-insensitive, but we'll normalize for Svix.
    return {k.lower(): v for k, v in headers.items()}


def verify_clerk_webhook(
    *,
    raw_body: bytes,
    headers: Mapping[str, str],
    secret: str,
) -> ClerkWebhookEvent:
    """
    Verify Svix signature and return a validated ClerkWebhookEvent.

    IMPORTANT:
    - `raw_body` must be the exact raw request body bytes.
    - `headers` must include: svix-id, svix-timestamp, svix-signature.
    """
    h = _normalize_headers(headers)

    svix_headers = {
        "svix-id": h.get("svix-id", ""),
        "svix-timestamp": h.get("svix-timestamp", ""),
        "svix-signature": h.get("svix-signature", ""),
    }

    missing = [k for k, v in svix_headers.items() if not v]
    if missing:
        raise WebhookSignatureError(metadata={"missing_headers": missing})

    try:
        wh = Webhook(secret)
        # Svix expects the *raw* payload string + the svix headers.
        verified = wh.verify(raw_body.decode("utf-8"), svix_headers)
    except Exception as e:
        raise WebhookSignatureError(str(e))

    # `verified` is usually a dict; normalize just in case.
    if isinstance(verified, dict):
        payload = verified
    elif isinstance(verified, (str, bytes)):
        payload = json.loads(verified)
    else:
        # last-resort: try to serialize
        payload = json.loads(json.dumps(verified))

    return ClerkWebhookEvent.model_validate(payload)
