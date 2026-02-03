from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import ParsingJobId, DocumentFileId
from app.domain.processing.models import ParsingJob
from app.domain.processing.enums import ParsingJobStatus
from .protocols import ParsingJobRepositoryProtocol

class ParsingJobRepository(ParsingJobRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: ParsingJob) -> ParsingJob:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: ParsingJobId) -> ParsingJob | None:
        return await self._db.get(ParsingJob, id)

    async def delete(self, id: ParsingJobId) -> None:
        job = await self.get_by_id(id)
        if job is not None:
            await self._db.delete(job)
            await self._db.flush()

    async def update(self, job: ParsingJob) -> ParsingJob:
        await self._db.flush()
        return job
    
    async def does_job_exist_for_message(self, messageId: str) -> bool:
        if not messageId:
            return False  # no message ID → no check

        stmt = select(ParsingJob.id).where(
            ParsingJob.pubsub_message_id == messageId
        ).limit(1)

        result = await self._db.execute(stmt)
        return result.scalar() is not None
    
    async def does_job_exist_for_file(self, id: DocumentFileId) -> bool:
        stmt = select(ParsingJob.id).where(
            ParsingJob.document_file_id == id,
            ParsingJob.status.in_([
                ParsingJobStatus.PENDING,
                ParsingJobStatus.QUEUED,
                ParsingJobStatus.PROCESSING,
                ParsingJobStatus.RETRYING
            ])
        ).limit(1).with_for_update(skip_locked=True)  # optional: avoid blocking if many concurrent checks

        result = await self._db.execute(stmt)
        return result.scalar() is not None