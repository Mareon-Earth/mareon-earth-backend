from __future__ import annotations

from abc import abstractmethod

from app.domain._shared.repository import BaseRepository
from app.domain._shared.types import ParsingJobId
from app.domain.processing.models import ParsingJob

from app.domain._shared.types import DocumentFileId

class ParsingJobRepositoryProtocol(BaseRepository[ParsingJob, ParsingJobId]):
    @abstractmethod
    async def update(self, job: ParsingJob) -> ParsingJob: ...
    async def does_job_exist_for_message(self, messageId: str) -> bool: ...
    async def does_job_exist_for_file(self, id: DocumentFileId) -> bool: ...
    