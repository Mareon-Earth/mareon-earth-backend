import base64
import json
import logging

from fastapi import APIRouter, Request, Response, status

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/pubsub")
async def pubsub_webhook(request: Request):
    """
    Handle Google Cloud Pub/Sub push messages.
    """
    try:
        body = await request.json()
    except Exception:
        logger.exception("Invalid JSON payload in Pub/Sub webhook")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    msg = (body or {}).get("message")
    if not isinstance(msg, dict):
        logger.error("Invalid Pub/Sub message format (missing 'message')")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    b64 = msg.get("data")
    if not b64:
        logger.error("Pub/Sub message missing 'data'")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    # 1) Decode base64 -> bytes
    try:
        raw_bytes = base64.b64decode(b64)
    except Exception:
        logger.exception("Failed to base64-decode Pub/Sub message.data")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    # 2) Bytes -> string (utf-8)
    try:
        raw_text = raw_bytes.decode("utf-8")
    except Exception:
        logger.exception("Failed to decode Pub/Sub message.data as utf-8")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    # 3) Parse JSON if possible (GCS JSON_API_V1 is JSON)
    decoded = None
    try:
        decoded = json.loads(raw_text)
    except Exception:
        # Not JSON — keep as text
        decoded = raw_text

    # Print/log both the wrapper and decoded payload
    print("Received Pub/Sub messageId=%s publishTime=%s attributes=%s",
                msg.get("messageId"), msg.get("publishTime"), msg.get("attributes"))

    print("Decoded message.data: %s", decoded)

    # If it *is* the GCS object JSON, you can also pull key fields:
    if isinstance(decoded, dict):
        logger.info("GCS event: bucket=%s name=%s generation=%s contentType=%s size=%s",
                    decoded.get("bucket"),
                    decoded.get("name"),
                    decoded.get("generation"),
                    decoded.get("contentType"),
                    decoded.get("size"))

    return Response(status_code=status.HTTP_204_NO_CONTENT)