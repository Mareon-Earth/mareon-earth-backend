from __future__ import annotations

import json
import logging
from typing import Any

from google.cloud import pubsub_v1
from google.api_core import exceptions as gcp_exceptions

from .enums import PubSubTopic
from .exceptions import PubSubConfigError, PubSubPublishError

logger = logging.getLogger(__name__)


class PubSubPublisher:
    def __init__(self, project_id: str) -> None:
        if not project_id:
            raise PubSubConfigError("project_id is required")
        self._project_id = project_id
        self._client = pubsub_v1.PublisherClient()

    @property
    def project_id(self) -> str:
        return self._project_id

    def _get_topic_path(self, topic: PubSubTopic) -> str:
        return self._client.topic_path(self._project_id, topic.value)

    def _serialize_data(self, data: dict[str, Any] | str | bytes) -> bytes:
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode("utf-8")
        if isinstance(data, dict):
            return json.dumps(data, default=str).encode("utf-8")
        raise PubSubPublishError(f"Unsupported data type: {type(data)}")

    async def publish(
        self,
        topic: PubSubTopic,
        data: dict[str, Any] | str | bytes,
        attributes: dict[str, str] | None = None,
        ordering_key: str | None = None,
    ) -> str:
        topic_path = self._get_topic_path(topic)
        serialized = self._serialize_data(data)

        try:
            future = self._client.publish(
                topic_path,
                serialized,
                ordering_key=ordering_key or "",
                **(attributes or {}),
            )
            message_id = future.result(timeout=30)
            logger.info("Published to %s: %s", topic.value, message_id)
            return message_id
        except Exception as e:
            raise PubSubPublishError(f"Publish failed: {e}", topic=topic.value, cause=e) from e

    async def publish_batch(self, topic: PubSubTopic, messages: list[dict[str, Any]]) -> list[str]:
        topic_path = self._get_topic_path(topic)
        futures = []

        for msg in messages:
            serialized = self._serialize_data(msg.get("data", {}))
            futures.append(self._client.publish(topic_path, serialized, **msg.get("attributes", {})))

        message_ids = []
        errors = []
        for i, future in enumerate(futures):
            try:
                message_ids.append(future.result(timeout=30))
            except Exception as e:
                errors.append(f"{i}: {e}")
                message_ids.append("")

        if errors:
            raise PubSubPublishError(f"Batch publish failures: {', '.join(errors)}", topic=topic.value)

        logger.info("Batch published %d messages to %s", len(message_ids), topic.value)
        return message_ids

    def close(self) -> None:
        self._client.stop()


class MockPubSubPublisher:
    """
    Mock publisher for testing.
    
    Records all published messages for assertion in tests.
    """

    def __init__(self, project_id: str = "test-project") -> None:
        self._project_id = project_id
        self._messages: list[dict[str, Any]] = []
        self._message_counter = 0

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def messages(self) -> list[dict[str, Any]]:
        """Get all published messages."""
        return self._messages.copy()

    def get_messages_for_topic(self, topic: PubSubTopic) -> list[dict[str, Any]]:
        """Get all messages published to a specific topic."""
        return [m for m in self._messages if m["topic"] == topic]

    def clear(self) -> None:
        """Clear all recorded messages."""
        self._messages.clear()
        self._message_counter = 0

    async def publish(
        self,
        topic: PubSubTopic,
        data: dict[str, Any] | str | bytes,
        attributes: dict[str, str] | None = None,
        ordering_key: str | None = None,
    ) -> str:
        self._message_counter += 1
        message_id = f"mock-{self._message_counter}"

        self._messages.append({
            "topic": topic,
            "data": data,
            "attributes": attributes or {},
            "ordering_key": ordering_key,
            "message_id": message_id,
        })

        logger.debug(
            "Mock published to %s: message_id=%s",
            topic.value,
            message_id,
        )
        return message_id

    async def publish_batch(
        self,
        topic: PubSubTopic,
        messages: list[dict[str, Any]],
    ) -> list[str]:
        message_ids = []
        for msg in messages:
            mid = await self.publish(
                topic,
                data=msg.get("data", {}),
                attributes=msg.get("attributes"),
            )
            message_ids.append(mid)
        return message_ids

    def close(self) -> None:
        """No-op for mock."""
        pass
