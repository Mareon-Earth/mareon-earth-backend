from __future__ import annotations

import base64
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .enums import PubSubSubscription


# ──────────────────────────────────────────────────────────────────────────────
# Incoming Message Types (from Pub/Sub push)
# ──────────────────────────────────────────────────────────────────────────────

class PubSubMessage(BaseModel):
    """
    The 'message' portion of a Pub/Sub push payload.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    message_id: str = Field(..., alias="messageId")
    publish_time: datetime = Field(..., alias="publishTime")
    data: str = Field(..., description="Base64-encoded message payload")
    attributes: dict[str, str] = Field(default_factory=dict)

    def decode_data_bytes(self) -> bytes:
        """Decode the base64 data field to raw bytes."""
        return base64.b64decode(self.data)

    def decode_data_text(self, encoding: str = "utf-8") -> str:
        """Decode the base64 data field to text."""
        return self.decode_data_bytes().decode(encoding)


class PubSubPushEnvelope(BaseModel):
    """
    Full Pub/Sub push webhook payload.
    
    This is what Cloud Run receives from Pub/Sub push subscriptions.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    message: PubSubMessage
    subscription: str  # full resource: projects/.../subscriptions/...

    @computed_field
    @property
    def subscription_short_name(self) -> str:
        """Extract the short subscription name from the full resource path."""
        return self.subscription.rsplit("/", 1)[-1]

    @computed_field
    @property
    def subscription_enum(self) -> PubSubSubscription | None:
        """Parse the subscription as an enum, or None if unknown."""
        return PubSubSubscription.from_resource_name(self.subscription)


# ──────────────────────────────────────────────────────────────────────────────
# GCS Notification Types
# ──────────────────────────────────────────────────────────────────────────────

GcsEventType = Literal[
    "OBJECT_FINALIZE",
    "OBJECT_DELETE", 
    "OBJECT_ARCHIVE",
    "OBJECT_METADATA_UPDATE",
]


class GcsAttributes(BaseModel):
    """
    Attributes from a GCS notification message.
    
    These are in the message.attributes field.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    bucket_id: str = Field(..., alias="bucketId")
    event_type: GcsEventType = Field(..., alias="eventType")
    event_time: datetime = Field(..., alias="eventTime")
    object_id: str = Field(..., alias="objectId")
    payload_format: Literal["JSON_API_V1", "NONE"] = Field(..., alias="payloadFormat")
    object_generation: str | None = Field(None, alias="objectGeneration")
    overwrote_generation: str | None = Field(None, alias="overwroteGeneration")


class GcsObjectMetadata(BaseModel):
    """
    Metadata of the GCS object from notification payload.
    
    This is parsed from message.data (after base64 decoding).
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    name: str  # full object path: org/.../files/...
    bucket: str
    content_type: str = Field(..., alias="contentType")
    size: str  # size in bytes as string
    time_created: datetime = Field(..., alias="timeCreated")
    updated: datetime
    generation: str
    metageneration: str
    
    # Optional fields
    md5_hash: str | None = Field(None, alias="md5Hash")
    crc32c: str | None = None
    etag: str | None = None
    storage_class: str | None = Field(None, alias="storageClass")
    
    # Custom metadata (x-goog-meta-* headers)
    metadata: dict[str, str] | None = None

    @property
    def size_bytes(self) -> int:
        """Get size as integer."""
        return int(self.size)

    @property
    def path_parts(self) -> list[str]:
        """Split the object name into path components."""
        return self.name.split("/")

    @property
    def filename(self) -> str:
        """Get just the filename from the object path."""
        return self.path_parts[-1] if self.path_parts else ""

    @property
    def directory(self) -> str:
        """Get the directory path (everything before the filename)."""
        parts = self.path_parts
        return "/".join(parts[:-1]) if len(parts) > 1 else ""


# ──────────────────────────────────────────────────────────────────────────────
# Outgoing Message Types (for publishing)
# ──────────────────────────────────────────────────────────────────────────────

class PublishMessage(BaseModel):
    """
    Message structure for batch publishing.
    
    Usage:
        messages = [
            PublishMessage(data={"doc_id": "123"}, attributes={"type": "pdf"}),
            PublishMessage(data={"doc_id": "456"}),
        ]
        await publisher.publish_batch(topic, [m.model_dump() for m in messages])
    """
    model_config = ConfigDict(extra="forbid")

    data: dict[str, str | int | float | bool | None] | str | bytes
    attributes: dict[str, str] = Field(default_factory=dict)
    ordering_key: str | None = None
