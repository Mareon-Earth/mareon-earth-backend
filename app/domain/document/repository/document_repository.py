from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.document.models import Document
from app.domain.document.repository.protocols import DocumentRepositoryProtocol

class DocumentRepository(DocumentRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: Document) -> Document:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: str) -> Document | None:
        return await self._db.get(Document, id)

    async def delete(self, id: str) -> None:
        doc = await self.get_by_id(id)
        if doc is not None:
            await self._db.delete(doc)
            await self._db.flush()

    async def update(self, document: Document) -> Document:
        await self._db.flush()
        return document
