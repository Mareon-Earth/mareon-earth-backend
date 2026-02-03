"""
Pub/Sub module for handling incoming messages and publishing outgoing messages.

Usage - Handling messages:
    from app.core.pubsub import (
        BasePubSubHandler,
        GcsUploadHandler,
        PubSubContext,
        PubSubSubscription,
        PubSubDropError,
        PubSubRetryableError,
        get_dispatcher,
    )
    
    class MyHandler(BasePubSubHandler):
        name = "my_handler"
        subscriptions = {PubSubSubscription.DOCUMENT_UPLOADS_API}
        
        async def handle(self, ctx: PubSubContext) -> None:
            # Process message...
    
    # Register at app startup
    get_dispatcher().register(MyHandler())

Usage - Publishing messages:
    from app.core.pubsub import PubSubPublisher, PubSubTopic
    
    publisher = PubSubPublisher(project_id="my-project")
    message_id = await publisher.publish(
        PubSubTopic.DOCUMENT_PROCESSED,
        data={"document_id": "123", "status": "completed"},
    )
"""

# Enums
from .enums import PubSubSubscription, PubSubTopic

# Context
from .context import PubSubContext

# Types (incoming and outgoing message structures)
from .types import (
    GcsAttributes,
    GcsEventType,
    GcsObjectMetadata,
    PublishMessage,
    PubSubMessage,
    PubSubPushEnvelope,
)

# Exceptions
from .exceptions import (
    PubSubConfigError,
    PubSubDropError,
    PubSubError,
    PubSubPublishError,
    PubSubRetryableError,
)

# Protocols
from .protocols import (
    PubSubDispatcherProtocol,
    PubSubHandlerProtocol,
    PubSubPublisherProtocol,
)

# Handler base classes
from .handlers import BasePubSubHandler, GcsUploadHandler

# Dispatcher
from .dispatcher import PubSubDispatcher, get_dispatcher, reset_dispatcher

# Publisher
from .publisher import MockPubSubPublisher, PubSubPublisher

# Setup and dependencies
from .setup import get_publisher, setup_pubsub, teardown_pubsub
from .dependencies import PubSubPublisherDep, get_pubsub_publisher

__all__ = [
    # Enums
    "PubSubSubscription",
    "PubSubTopic",
    # Context
    "PubSubContext",
    # Types
    "GcsAttributes",
    "GcsEventType",
    "GcsObjectMetadata",
    "PublishMessage",
    "PubSubMessage",
    "PubSubPushEnvelope",
    # Exceptions
    "PubSubConfigError",
    "PubSubDropError",
    "PubSubError",
    "PubSubPublishError",
    "PubSubRetryableError",
    # Protocols
    "PubSubDispatcherProtocol",
    "PubSubHandlerProtocol",
    "PubSubPublisherProtocol",
    # Handler base classes
    "BasePubSubHandler",
    "GcsUploadHandler",
    # Dispatcher
    "PubSubDispatcher",
    "get_dispatcher",
    "reset_dispatcher",
    # Publisher
    "MockPubSubPublisher",
    "PubSubPublisher",
    # Setup and dependencies
    "get_publisher",
    "setup_pubsub",
    "teardown_pubsub",
    "PubSubPublisherDep",
    "get_pubsub_publisher",
]
