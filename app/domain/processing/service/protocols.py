from typing import Protocol
from app.domain.processing.schemas import ParsingJobCreate, ParsingJobRead


class ParsingJobServiceProtocol(Protocol):
    async def create_job(self, job: ParsingJobCreate) -> ParsingJobRead: ...