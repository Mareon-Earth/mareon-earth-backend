from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from .enums import PubSubSubscription


@dataclass(frozen=True)
class PubSubContext:
    # subscription
    subscription_resource: str                  # full: projects/.../subscriptions/...
    subscription: PubSubSubscription | None     # parsed enum, None if unknown
    subscription_short_name: str                # last segment

    # message metadata
    message_id: str
    publish_time: datetime
    attributes: Mapping[str, str]

    # decoded payload
    data_raw: bytes                             # base64 decoded bytes
    data_text: str | None                       # utf-8 decoded text, if possible
    data_json: Any | None                       # parsed JSON if possible (dict/list), else None
