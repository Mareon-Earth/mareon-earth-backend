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
        logger.error("Invalid JSON payload in Pub/Sub webhook")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    if not body or "message" not in body:
        logger.error("Invalid Pub/Sub message format")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    message = body["message"]
    print(f"Received Pub/Sub message: {message}")    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    