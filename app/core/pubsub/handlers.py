from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from .context import PubSubContext
from .enums import PubSubSubscription

class BasePubSubHandler(ABC):
    name: ClassVar[str]
    subscriptions: ClassVar[set[PubSubSubscription]]

    def matches(self, ctx: PubSubContext) -> bool:
        return ctx.subscription in self.subscriptions

    @abstractmethod
    async def handle(self, ctx: PubSubContext) -> None:
        ...

class GcsUploadHandler(BasePubSubHandler):
    allowed_prefixes: ClassVar[set[str]] = set()
    allowed_content_types: ClassVar[set[str]] = set()

    def matches(self, ctx: PubSubContext) -> bool:
        if ctx.event_type != "OBJECT_FINALIZE":
            return False

        if not super().matches(ctx):
            return False

        if self.allowed_prefixes:
            object_id = ctx.object_id or ""
            if not any(object_id.startswith(p) for p in self.allowed_prefixes):
                return False
        return True

    async def handle(self, ctx: PubSubContext) -> None:
        from .types import GcsObjectMetadata
        from .exceptions import PubSubDropError

        try:
            metadata = ctx.parse_as(GcsObjectMetadata)
        except Exception as e:
            raise PubSubDropError(f"Failed to parse GCS metadata: {e}") from e

        if self.allowed_content_types and metadata.content_type not in self.allowed_content_types:
            raise PubSubDropError(f"Content type {metadata.content_type} not allowed")

        await self.handle_upload(ctx, metadata)

    @abstractmethod
    async def handle_upload(self, ctx: PubSubContext, metadata: "GcsObjectMetadata") -> None:
        ...

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .types import GcsObjectMetadata
