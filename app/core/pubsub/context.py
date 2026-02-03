from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel

from .enums import PubSubSubscription

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class PubSubContext:
    subscription_resource: str
    subscription: PubSubSubscription | None
    subscription_short_name: str
    message_id: str
    publish_time: datetime
    attributes: dict[str, str] = field(default_factory=dict)
    data_raw: bytes = field(default=b"")
    data_text: str | None = None
    data_json: Any | None = None

    def parse_as(self, model: type[T]) -> T:
        if self.data_json is None or not isinstance(self.data_json, dict):
            raise ValueError("JSON data not available or invalid")
        return model.model_validate(self.data_json)

    def get_attribute(self, key: str, default: str | None = None) -> str | None:
        return self.attributes.get(key, default)

    @property
    def event_type(self) -> str | None:
        return self.attributes.get("eventType")

    @property
    def bucket_id(self) -> str | None:
        return self.attributes.get("bucketId")

    @property
    def object_id(self) -> str | None:
        return self.attributes.get("objectId")

    @classmethod
    def from_push_message(
        cls,
        subscription: str,
        message_id: str,
        publish_time: datetime,
        data_b64: str,
        attributes: dict[str, str] | None = None,
    ) -> PubSubContext:
        attributes = attributes or {}
        subscription_short = subscription.rsplit("/", 1)[-1]
        subscription_enum = PubSubSubscription.from_resource_name(subscription)

        try:
            data_raw = base64.b64decode(data_b64)
        except Exception:
            data_raw = b""

        data_text = None
        try:
            data_text = data_raw.decode("utf-8")
        except Exception:
            pass

        data_json = None
        if data_text:
            try:
                data_json = json.loads(data_text)
            except Exception:
                pass

        return cls(
            subscription_resource=subscription,
            subscription=subscription_enum,
            subscription_short_name=subscription_short,
            message_id=message_id,
            publish_time=publish_time,
            attributes=attributes,
            data_raw=data_raw,
            data_text=data_text,
            data_json=data_json,
        )
