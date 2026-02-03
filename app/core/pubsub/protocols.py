from __future__ import annotations

from typing import Protocol, runtime_checkable

from .context import PubSubContext
from .enums import PubSubSubscription


@runtime_checkable
class PubSubHandlerProtocol(Protocol):
    """
    Implementations live outside core (usually domain/*).
    Keep matching logic small and explicit.
    """

    name: str
    subscriptions: set[PubSubSubscription]

    def matches(self, ctx: PubSubContext) -> bool:
        """
        Return True if this handler should run for the given message.
        You can check ctx.subscription, ctx.attributes, payload shape, etc.
        """
        ...

    async def handle(self, ctx: PubSubContext) -> None:
        """
        Perform the work. Raise:
          - PubSubDropError -> 204 (no retry)
          - PubSubRetryableError -> 500 (retry)
        """
        ...
