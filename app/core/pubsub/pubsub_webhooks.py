import logging

from fastapi import APIRouter, Request, Response, status
from pydantic import ValidationError

from app.core.pubsub import (
    PubSubContext,
    PubSubPushEnvelope,
    PubSubRetryableError,
    get_dispatcher,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/pubsub")
async def pubsub_webhook(request: Request) -> Response:
    try:
        body = await request.json()
        envelope = PubSubPushEnvelope.model_validate(body)
        ctx = PubSubContext.from_push_message(
            subscription=envelope.subscription,
            message_id=envelope.message.message_id,
            publish_time=envelope.message.publish_time,
            data_b64=envelope.message.data,
            attributes=envelope.message.attributes,
        )
    except Exception:
        logger.exception("Invalid Pub/Sub payload")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    logger.info("Pub/Sub message: sub=%s id=%s", ctx.subscription_short_name, ctx.message_id)

    try:
        await get_dispatcher().dispatch(ctx)
    except PubSubRetryableError as e:
        logger.error("Retryable error: %s", e)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
