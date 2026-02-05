from __future__ import annotations

from app.domain._shared.types import DateTime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, computed_field
from uuid import UUID

from app.domain.processing.enums import ParsingJobStatus


class ParsingJobBase(BaseModel):
    """Base schema for a parsing job."""
    org_id: UUID = Field(..., description="Organization UUID")
    document_file_id: UUID = Field(..., description="The file being parsed")

    pubsub_message_id: Optional[str] = Field(None, description="Pub/Sub message ID.")
    pubsub_publish_time: Optional[DateTime] = Field(None, description="Pub/Sub publish timestamp.")

    source_gcs_uri: Optional[str] = Field(None, description="Full GCS URI of the source file.")
    result_gcs_uri: Optional[str] = Field(
        None,
        description="GCS URI where parsing results should be uploaded."
    )


class ParsingJobCreate(ParsingJobBase):
    """Input schema when creating a new ParsingJob."""
    pass


class ParsingJobRead(ParsingJobBase):
    """Full output schema for a parsing job."""
    id: UUID = Field(..., description="Parsing job UUID")

    status: ParsingJobStatus
    attempt_count: int
    max_attempts: int

    started_at: Optional[DateTime]
    finished_at: Optional[DateTime]

    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]

    created_at: DateTime
    updated_at: DateTime

    @computed_field
    @property
    def duration_ms(self) -> Optional[int]:
        """Compute duration from started_at and finished_at."""
        if self.started_at and self.finished_at:
            delta = self.finished_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return None

    class Config:
        from_attributes = True


class ParsingJobStatusUpdate(BaseModel):
    """Schema for updating parsing job status (used by workers)."""
    status: ParsingJobStatus
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    result_gcs_uri: Optional[str] = Field(
        None,
        description="Final result URI (can be updated by worker if different from predefined)"
    )