from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from .context import PubSubContext
from .enums import PubSubSubscription, PubSubTopic


@runtime_checkable
class PubSubHandlerProtocol(Protocol):
    """
    Protocol for Pub/Sub message handlers.
    
    Implementations should:
    1. Define which subscriptions they handle via `subscriptions`
    2. Optionally refine matching logic in `matches()`
    3. Implement the actual processing in `handle()`
    
    Example:
        class GcsUploadHandler:
            name = "gcs_upload_handler"
            subscriptions = {PubSubSubscription.DOCUMENT_UPLOADS_API}
            
            def matches(self, ctx: PubSubContext) -> bool:
                # Only handle OBJECT_FINALIZE events
                return ctx.attributes.get("eventType") == "OBJECT_FINALIZE"
            
            async def handle(self, ctx: PubSubContext) -> None:
                # Process the upload...
    """

    @property
    def name(self) -> str:
        """Unique identifier for this handler (used in logging)."""
        ...

    @property
    def subscriptions(self) -> set[PubSubSubscription]:
        """Set of subscriptions this handler can process."""
        ...

    def matches(self, ctx: PubSubContext) -> bool:
        """
        Return True if this handler should process the message.
        
        Default behavior: return True if subscription matches.
        Override for finer-grained control (e.g., check attributes, payload shape).
        """
        ...

    async def handle(self, ctx: PubSubContext) -> None:
        """
        Process the message.
        
        Raises:
            PubSubDropError: Message is invalid/not relevant. Returns 204 (no retry).
            PubSubRetryableError: Transient failure. Returns 500 (Pub/Sub retries).
        """
        ...


@runtime_checkable
class PubSubPublisherProtocol(Protocol):
    """
    Protocol for publishing messages to Pub/Sub topics.
    
    Implementations can be:
    - GCP Pub/Sub client (production)
    - In-memory mock (testing)
    - Local emulator client (development)
    """

    @abstractmethod
    async def publish(
        self,
        topic: PubSubTopic,
        data: dict[str, Any] | str | bytes,
        attributes: dict[str, str] | None = None,
        ordering_key: str | None = None,
    ) -> str:
        """
        Publish a message to the specified topic.
        
        Args:
            topic: The topic to publish to
            data: Message payload (dict will be JSON-serialized)
            attributes: Optional message attributes
            ordering_key: Optional ordering key for ordered delivery
            
        Returns:
            The published message ID
            
        Raises:
            PubSubPublishError: If publishing fails
        """
        ...

    @abstractmethod
    async def publish_batch(
        self,
        topic: PubSubTopic,
        messages: list[dict[str, Any]],
    ) -> list[str]:
        """
        Publish multiple messages to a topic efficiently.
        
        Args:
            topic: The topic to publish to
            messages: List of message dicts with 'data' and optional 'attributes'
            
        Returns:
            List of published message IDs
        """
        ...


class PubSubDispatcherProtocol(Protocol):
    """Protocol for the message dispatcher that routes to handlers."""

    def register(self, handler: PubSubHandlerProtocol) -> None:
        """Register a handler with the dispatcher."""
        ...

    async def dispatch(self, ctx: PubSubContext) -> bool:
        """
        Dispatch a message to matching handlers.
        
        Returns:
            True if at least one handler processed the message
        """
        ...
