from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

from app.domain.processing.enums import ParsingJobStatus


class ParsingJobBase(BaseModel):
    """
    Base schema with shared fields used by both ParsingJobCreate and ParsingJobRead.
    Contains the core identifying and tracking fields.
    """
    org_id: UUID = Field(..., description="Organization UUID")
    document_id: Optional[UUID] = Field(None, description="Parent document if known")
    document_file_id: UUID = Field(..., description="The file being parsed")

    pubsub_message_id: Optional[str] = Field(None, description="Pub/Sub message ID (for debugging/idempotency)")
    pubsub_publish_time: Optional[datetime] = Field(None, description="Pub/Sub publish timestamp")

    source_gcs_object: Optional[str] = Field(None, description="Full GCS object path of the source file")

    result_gcs_bucket: Optional[str] = Field(None, description="Bucket where parsing result JSON was stored")
    result_gcs_prefix: Optional[str] = Field(None, description="Prefix/path to the parsing result in GCS")

class ParsingJobCreate(ParsingJobBase):
    """
    Input schema when creating a new ParsingJob.
    No DB-generated fields are included.
    """
    pass  # inherits everything — nothing extra needed


class ParsingJobRead(ParsingJobBase):
    """
    Full output schema — what you return after creation or when reading a job.
    """
    id: UUID = Field(..., description="Parsing job UUID")

    status: ParsingJobStatus
    attempt_count: int
    max_attempts: int

    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    duration_ms: Optional[int]

    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows .model_validate(db_obj) / from_orm