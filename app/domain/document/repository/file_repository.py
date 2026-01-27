from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.document.models import DocumentFile
from app.domain.document.repository.protocols import DocumentFileRepositoryProtocol
from app.domain._shared.types import DocumentFileId

class DocumentFileRepository(DocumentFileRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: DocumentFile) -> DocumentFile:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: DocumentFileId) -> DocumentFile | None:
        return await self._db.get(DocumentFile, id)

    async def delete(self, id: DocumentFileId) -> None:
        doc = await self.get_by_id(id)
        if doc is not None:
            await self._db.delete(doc)
            await self._db.flush()

    async def update(self, file: DocumentFile) -> DocumentFile:
        await self._db.flush()
        return file
