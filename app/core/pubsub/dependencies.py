"""
FastAPI dependencies for Pub/Sub.

Usage in routers:
    from app.core.pubsub.dependencies import PubSubPublisherDep
    
    @router.post("/documents/{doc_id}/process")
    async def process_document(
        doc_id: str,
        publisher: PubSubPublisherDep,
    ):
        await publisher.publish(
            PubSubTopic.DOCUMENT_PROCESSING,
            data={"document_id": doc_id},
        )
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from .protocols import PubSubPublisherProtocol
from .setup import get_publisher


def get_pubsub_publisher() -> PubSubPublisherProtocol:
    """FastAPI dependency to get the Pub/Sub publisher."""
    return get_publisher()


# Type alias for dependency injection
PubSubPublisherDep = Annotated[PubSubPublisherProtocol, Depends(get_pubsub_publisher)]
