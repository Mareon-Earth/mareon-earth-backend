from __future__ import annotations

import base64
from datetime import datetime
from typing import Dict, Literal, Optional, Union

from pydantic import BaseModel, Field, validator, root_validator

class PubSubMessage(BaseModel):
    messageId: str = Field(..., alias="messageId")
    publishTime: datetime = Field(..., alias="publishTime")
    data: str                                      # base64 encoded string
    attributes: Dict[str, str] = Field(default_factory=dict)

class PubSubPushEnvelope(BaseModel):
    """Full Pub/Sub push payload"""
    message: PubSubMessage
    subscription: str

class GcsAttributes(BaseModel):
    bucketId: str
    eventType: Literal["OBJECT_FINALIZE", "OBJECT_DELETE", "OBJECT_METADATA_UPDATE"]
    eventTime: datetime
    objectId: str
    payloadFormat: Literal["JSON_API_V1", "NONE"]

class GcsObjectMetadata(BaseModel):
    """Metadata of the GCS object from notification (decoded message.data)"""
    id: str
    name: str                                      # full path: org/.../files/...
    bucket: str
    contentType: str
    timeCreated: datetime