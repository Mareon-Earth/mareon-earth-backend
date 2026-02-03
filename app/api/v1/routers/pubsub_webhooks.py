import base64
import json
import logging

from fastapi import APIRouter, Request, Response, status
from pydantic import ValidationError

from app.core.pubsub import PubSubPushEnvelope, GcsObjectMetadata

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/pubsub")
async def pubsub_webhook(request: Request):
    try:
        body = await request.json()
    except Exception:
        logger.exception("Invalid JSON payload in Pub/Sub webhook")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        env = PubSubPushEnvelope.model_validate(body)  # ignores extra keys
    except ValidationError:
        logger.exception("Invalid Pub/Sub message format")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    b64 = env.message.data
    if not b64:
        logger.error("Pub/Sub message missing 'data'")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        raw_text = base64.b64decode(b64).decode("utf-8")
    except Exception:
        logger.exception("Failed to decode Pub/Sub message.data")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        decoded = json.loads(raw_text)
    except Exception:
        decoded = raw_text

    # same intent as before: print wrapper + decoded payload
    print(env.message.model_dump(by_alias=True))
    print("Decoded message.data:", decoded)

    # map decoded -> your model (ignore extra fields)
    if isinstance(decoded, dict):
        try:
            meta = GcsObjectMetadata.model_validate(decoded)
            logger.info("GCS event: bucket=%s name=%s contentType=%s",
                        meta.bucket, meta.name, meta.contentType)
        except ValidationError:
            pass

    return Response(status_code=status.HTTP_204_NO_CONTENT)
