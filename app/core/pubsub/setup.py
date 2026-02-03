"""
Pub/Sub setup module - registers all handlers at application startup.

Import and call `setup_pubsub()` in your main.py or app factory.

Usage:
    from app.core.pubsub.setup import setup_pubsub
    from app.infrastructure.db import session_manager
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        setup_pubsub(
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            session_manager=session_manager,
        )
        yield
        # Shutdown
        teardown_pubsub()
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .dispatcher import get_dispatcher
from .publisher import PubSubPublisher, MockPubSubPublisher

if TYPE_CHECKING:
    from app.infrastructure.db.session_manager import SessionManager

logger = logging.getLogger(__name__)

# Global publisher instance
_publisher: PubSubPublisher | MockPubSubPublisher | None = None

def setup_pubsub(
    project_id: str | None = None,
    session_manager: "SessionManager | None" = None,
    use_mock_publisher: bool = False,
) -> None:
    global _publisher
    dispatcher = get_dispatcher()

    if use_mock_publisher:
        _publisher = MockPubSubPublisher()
        logger.info("Using mock Pub/Sub publisher")
    elif project_id:
        _publisher = PubSubPublisher(project_id=project_id)
        logger.info("Initialized Pub/Sub publisher for %s", project_id)
    else:
        logger.warning("Pub/Sub publisher not initialized (no project_id)")

    # Fallback to global AsyncSessionLocal if not provided
    if session_manager is None:
        try:
            from app.infrastructure.db.session_manager import AsyncSessionLocal
            session_manager = AsyncSessionLocal
            logger.info("Using global AsyncSessionLocal for Pub/Sub handlers")
        except ImportError:
            logger.warning("Could not import AsyncSessionLocal")

    if session_manager:
        from app.domain.document.handlers import DocumentUploadHandler
        dispatcher.register(DocumentUploadHandler(session_manager))
        logger.info("Registered DocumentUploadHandler")
    else:
        logger.warning("session_manager missing, skipping handler registration")

    logger.info("Pub/Sub setup complete")


def get_publisher() -> PubSubPublisher | MockPubSubPublisher:
    """Get the global publisher instance."""
    if _publisher is None:
        raise RuntimeError("Pub/Sub not initialized. Call setup_pubsub() first.")
    return _publisher


def teardown_pubsub() -> None:
    """Cleanup Pub/Sub resources (call at shutdown)."""
    global _publisher
    if _publisher is not None:
        _publisher.close()
        _publisher = None
        logger.info("Pub/Sub publisher closed")


# Import for type checking
from .dispatcher import PubSubDispatcher