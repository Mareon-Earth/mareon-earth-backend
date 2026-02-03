from __future__ import annotations


class PubSubError(Exception):
    """Base Pub/Sub handling error."""


class PubSubDropError(PubSubError):
    """
    Message is invalid / not relevant / cannot be processed.
    Router should return 204 so Pub/Sub does NOT retry.
    """


class PubSubRetryableError(PubSubError):
    """
    Transient failure (DB down, network error, etc).
    Router should return 500 so Pub/Sub retries.
    """
