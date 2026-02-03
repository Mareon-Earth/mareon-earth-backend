from __future__ import annotations

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.processing.models import ParsingJob
from app.domain.processing.schemas import ParsingJobCreate, ParsingJobRead
from app.domain.processing.repository import ParsingJobRepositoryProtocol
from app.domain.processing.enums import ParsingJobStatus
import app.domain.processing.exceptions as exc
from .protocols import ParsingJobServiceProtocol

class ParsingJobService(ParsingJobServiceProtocol):
    """
    Application service for document flows.

    Note:
    - This service is request-scoped (it holds an AsyncSession).
    - Routers should be thin wrappers: `return await svc.method(payload)`
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        jobs: ParsingJobRepositoryProtocol,
    ):
        self._db = db
        self._jobs = jobs

async def create_job(self, job: ParsingJobCreate) -> ParsingJobRead:
    """
    Creates a new parsing job from the given input schema.
    
    - Checks for existing job by pub/sub message ID (idempotency for Pub/Sub retries)
    - Checks for existing active job for the same file (prevents duplicates)
    - Creates new job in PENDING state if no conflict
    - Returns the full read representation
    """
    # 1. Fast path: check if this exact Pub/Sub message already created a job
    if job.pubsub_message_id:
        if await self._jobs.does_job_exist_for_message(str(job.pubsub_message_id)):
            raise exc.ParsingJobAlreadyExistsError

    # 2. Secondary check: prevent multiple active jobs for the same file
    if await self._jobs.does_job_exist_for_file(str(job.document_file_id)):
        raise exc.ParsingJobAlreadyExistsError

    # 3. Create new job
    new_job = ParsingJob(
        org_id=str(job.org_id),                     # UUID → str (DB column is String)
        document_file_id=str(job.document_file_id),
        document_id=str(job.document_id) if job.document_id else None,
        
        # Pub/Sub tracking (only set if provided)
        pubsub_message_id=job.pubsub_message_id,
        pubsub_publish_time=job.pubsub_publish_time,
        source_gcs_object=job.source_gcs_object,
        
        # Result fields start empty — worker sets them later
        result_gcs_bucket=None,
        result_gcs_prefix=None,
        
        # Default state
        status=ParsingJobStatus.PENDING,
        attempt_count=0,
    )

    # 4. Persist & refresh
    created = await self._jobs.create(new_job)
    await self._db.refresh(created)  # get id, created_at, updated_at

    # 5. Return read schema
    return ParsingJobRead.model_validate(created)