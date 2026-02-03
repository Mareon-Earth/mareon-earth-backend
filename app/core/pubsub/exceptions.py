from __future__ import annotations


class PubSubError(Exception):
    """Base Pub/Sub error."""


# ──────────────────────────────────────────────────────────────────────────────
# Handler Errors (used by message handlers)
# ──────────────────────────────────────────────────────────────────────────────

class PubSubDropError(PubSubError):
    """
    Message is invalid, not relevant, or cannot be processed.
    
    When raised, the router returns 204 so Pub/Sub does NOT retry.
    Use for:
    - Malformed messages
    - Messages that don't match expected format
    - Messages for unknown/unsupported event types
    - Business logic rejection (e.g., duplicate processing)
    """


class PubSubRetryableError(PubSubError):
    """
    Transient failure that should be retried.
    
    When raised, the router returns 500 so Pub/Sub retries with backoff.
    Use for:
    - Database connection failures
    - External service unavailable
    - Rate limiting
    - Temporary resource exhaustion
    """


# ──────────────────────────────────────────────────────────────────────────────
# Publisher Errors (used by message publisher)
# ──────────────────────────────────────────────────────────────────────────────

class PubSubPublishError(PubSubError):
    """
    Failed to publish a message to Pub/Sub.
    
    Contains details about the failure for logging/debugging.
    """
    def __init__(
        self,
        message: str,
        topic: str | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.topic = topic
        self.cause = cause

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.topic:
            parts.append(f"topic={self.topic}")
        if self.cause:
            parts.append(f"cause={self.cause!r}")
        return " | ".join(parts)


class PubSubConfigError(PubSubError):
    """
    Configuration error (e.g., missing project ID, invalid topic).
    
    This is a programming/deployment error, not a runtime error.
    """
