from __future__ import annotations

import base64
from datetime import datetime
from typing import Dict, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .enums import PubSubSubscription


class PubSubMessage(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    message_id: str = Field(..., alias="messageId")
    publish_time: datetime = Field(..., alias="publishTime")
    data: str = Field(..., description="Base64-encoded message payload")
    attributes: Dict[str, str] = Field(default_factory=dict)

    def decode_data_bytes(self) -> bytes:
        return base64.b64decode(self.data)

    def decode_data_text(self, encoding: str = "utf-8") -> str:
        return self.decode_data_bytes().decode(encoding)


class PubSubPushEnvelope(BaseModel):
    """Full Pub/Sub push payload"""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    message: PubSubMessage
    subscription: str  # full resource: projects/.../subscriptions/...

    @computed_field
    @property
    def subscription_short_name(self) -> str:
        return self.subscription.rsplit("/", 1)[-1]

    @computed_field
    @property
    def subscription_enum(self) -> PubSubSubscription | None:
        return PubSubSubscription.from_resource_name(self.subscription)


class GcsAttributes(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    bucket_id: str = Field(..., alias="bucketId")
    event_type: Literal["OBJECT_FINALIZE", "OBJECT_DELETE", "OBJECT_METADATA_UPDATE"] = Field(..., alias="eventType")
    event_time: datetime = Field(..., alias="eventTime")
    object_id: str = Field(..., alias="objectId")
    payload_format: Literal["JSON_API_V1", "NONE"] = Field(..., alias="payloadFormat")


class GcsObjectMetadata(BaseModel):
    """Metadata of the GCS object from notification (decoded message.data)"""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    name: str  # full path: org/.../files/...
    bucket: str
    content_type: str = Field(..., alias="contentType")
    time_created: datetime = Field(..., alias="timeCreated")
