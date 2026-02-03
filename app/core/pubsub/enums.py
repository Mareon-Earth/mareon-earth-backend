from __future__ import annotations

from enum import StrEnum


class PubSubSubscription(StrEnum):
    """
    Use the *short* Pub/Sub subscription name (last segment).
    This keeps things stable across projects/environments.
    """
    DOCUMENT_UPLOADS_API_SUB = "mareon-prod-document-uploads-api-sub"

    @classmethod
    def from_resource_name(cls, resource_name: str) -> "PubSubSubscription | None":
        """
        Input:  'projects/.../subscriptions/<short-name>'
        Output: PubSubSubscription or None if unknown.
        """
        short = resource_name.rsplit("/", 1)[-1]
        try:
            return cls(short)
        except ValueError:
            return None
