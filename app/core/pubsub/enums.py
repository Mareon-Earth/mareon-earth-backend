from __future__ import annotations

from enum import StrEnum


class PubSubTopic(StrEnum):
    """
    Pub/Sub topic names (short names, last segment).
    Used for publishing messages.
    """
    DOCUMENT_UPLOADS = "mareon-prod-document-uploads"
    # Add more topics as needed:
    # DOCUMENT_PROCESSED = "mareon-prod-document-processed"
    # VESSEL_UPDATES = "mareon-prod-vessel-updates"

    def full_name(self, project_id: str) -> str:
        """Returns the full topic resource name."""
        return f"projects/{project_id}/topics/{self.value}"


class PubSubSubscription(StrEnum):
    """
    Pub/Sub subscription names (short names, last segment).
    Used for routing incoming messages to handlers.
    """
    DOCUMENT_UPLOADS_API = "mareon-prod-document-uploads-api-sub"
    # Add more subscriptions as needed:
    # DOCUMENT_PROCESSED_INGESTION = "mareon-prod-document-processed-ingestion-sub"

    @classmethod
    def from_resource_name(cls, resource_name: str) -> PubSubSubscription | None:
        """
        Parse subscription enum from full resource name.
        Input:  'projects/.../subscriptions/<short-name>'
        Output: PubSubSubscription or None if unknown.
        """
        short = resource_name.rsplit("/", 1)[-1]
        try:
            return cls(short)
        except ValueError:
            return None

    def full_name(self, project_id: str) -> str:
        """Returns the full subscription resource name."""
        return f"projects/{project_id}/subscriptions/{self.value}"
