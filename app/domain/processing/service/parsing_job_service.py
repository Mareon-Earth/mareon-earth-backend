from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.processing.models import ParsingJob
from app.domain.processing.schemas import ParsingJobCreate, ParsingJobRead
from app.domain.processing.repository import ParsingJobRepositoryProtocol
from app.domain.processing.enums import ParsingJobStatus
from app.domain._shared.gcs import build_parsing_result_uri_from_source
import app.domain.processing.exceptions as exc
from .protocols import ParsingJobServiceProtocol


class ParsingJobService(ParsingJobServiceProtocol):
    """
    Application service for parsing job operations.

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
        - Predefines the result_gcs_uri so worker knows where to upload
        - Returns the full read representation
        """
        # 1. Fast path: check if this exact Pub/Sub message already created a job
        if job.pubsub_message_id:
            if await self._jobs.does_job_exist_for_message(job.pubsub_message_id):
                raise exc.ParsingJobAlreadyExistsError

        # 2. Secondary check: prevent multiple active jobs for the same file
        if await self._jobs.does_job_exist_for_file(str(job.document_file_id)):
            raise exc.ParsingJobAlreadyExistsError

        # 3. Compute result_gcs_uri if source_gcs_uri is provided
        result_gcs_uri = None
        if job.source_gcs_uri:
            result_gcs_uri = job.result_gcs_uri or build_parsing_result_uri_from_source(
                source_uri=job.source_gcs_uri,
                document_id=str(job.document_file_id),
                file_id=str(job.document_file_id),
            )

        # 4. Create new job
        new_job = ParsingJob(
            org_id=str(job.org_id),
            document_file_id=str(job.document_file_id),
            
            # Pub/Sub tracking
            pubsub_message_id=job.pubsub_message_id,
            pubsub_publish_time=job.pubsub_publish_time,
            
            # Storage URIs - result_gcs_uri is predefined
            source_gcs_uri=job.source_gcs_uri,
            result_gcs_uri=result_gcs_uri,
            
            # Default state
            status=ParsingJobStatus.PENDING,
            attempt_count=0,
        )

        # 5. Persist & refresh
        created = await self._jobs.create(new_job)
        await self._db.refresh(created)

        # 6. Return read schema
        return ParsingJobRead.model_validate(created)