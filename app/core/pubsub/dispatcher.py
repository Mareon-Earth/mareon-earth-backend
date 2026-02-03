from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING

from .context import PubSubContext
from .enums import PubSubSubscription
from .exceptions import PubSubDropError, PubSubRetryableError

if TYPE_CHECKING:
    from .protocols import PubSubHandlerProtocol

logger = logging.getLogger(__name__)

class PubSubDispatcher:
    def __init__(self) -> None:
        self._handlers: dict[PubSubSubscription, list[PubSubHandlerProtocol]] = defaultdict(list)
        self._all_handlers: list[PubSubHandlerProtocol] = []

    def register(self, handler: PubSubHandlerProtocol) -> None:
        self._all_handlers.append(handler)
        for sub in handler.subscriptions:
            self._handlers[sub].append(handler)
            logger.info("Registered handler %r for subscription %s", handler.name, sub.value)

    def get_handlers(self, subscription: PubSubSubscription | None) -> list[PubSubHandlerProtocol]:
        return self._handlers.get(subscription, []) if subscription else []

    async def dispatch(self, ctx: PubSubContext) -> bool:
        if not ctx.subscription:
            logger.warning("Unknown subscription %s", ctx.subscription_short_name)
            return False

        handlers = self.get_handlers(ctx.subscription)
        if not handlers:
            logger.warning("No handlers for %s", ctx.subscription.value)
            return False

        processed = False
        retryable_errors = []

        for handler in handlers:
            try:
                if not handler.matches(ctx):
                    continue

                await handler.handle(ctx)
                processed = True
                logger.info("Handler %s processed message %s", handler.name, ctx.message_id)

            except PubSubDropError as e:
                logger.warning("Handler %s dropped message: %s", handler.name, e)
            except PubSubRetryableError as e:
                logger.error("Handler %s failed (retryable): %s", handler.name, e)
                retryable_errors.append(e)
            except Exception as e:
                logger.exception("Handler %s unexpected error", handler.name)
                retryable_errors.append(PubSubRetryableError(f"Unexpected: {e}"))

        if retryable_errors:
            raise PubSubRetryableError(f"Errors in handlers: {retryable_errors}")

        return processed

_dispatcher: PubSubDispatcher | None = None

def get_dispatcher() -> PubSubDispatcher:
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = PubSubDispatcher()
    return _dispatcher

def reset_dispatcher() -> None:
    global _dispatcher
    _dispatcher = None
