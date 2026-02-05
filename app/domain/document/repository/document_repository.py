from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import DocumentId, OrganizationId
from app.domain.document.enums import DocumentType
from app.domain.document.models import Document
from app.domain.document.repository.protocols import DocumentRepositoryProtocol


class DocumentRepository(DocumentRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: Document) -> Document:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: DocumentId) -> Document | None:
        return await self._db.get(Document, id)

    async def delete(self, id: DocumentId) -> None:
        doc = await self.get_by_id(id)
        if doc is not None:
            await self._db.delete(doc)
            await self._db.flush()

    async def update(self, document: Document) -> Document:
        await self._db.flush()
        return document

    def _build_filters(
        self,
        org_id: OrganizationId,
        *,
        document_type: DocumentType | None = None,
        search: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list:
        """Build common filter conditions."""
        filters = [Document.org_id == org_id]

        if document_type is not None:
            filters.append(Document.document_type == document_type)

        if search:
            filters.append(Document.title.ilike(f"%{search}%"))

        if created_after is not None:
            filters.append(Document.created_at >= created_after)

        if created_before is not None:
            filters.append(Document.created_at <= created_before)

        return filters

    async def list_by_org(
        self,
        org_id: OrganizationId,
        *,
        document_type: DocumentType | None = None,
        search: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Document]:
        filters = self._build_filters(
            org_id,
            document_type=document_type,
            search=search,
            created_after=created_after,
            created_before=created_before,
        )

        stmt = (
            select(Document)
            .where(*filters)
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_org(
        self,
        org_id: OrganizationId,
        *,
        document_type: DocumentType | None = None,
        search: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        filters = self._build_filters(
            org_id,
            document_type=document_type,
            search=search,
            created_after=created_after,
            created_before=created_before,
        )

        stmt = select(func.count()).select_from(Document).where(*filters)
        result = await self._db.execute(stmt)
        return result.scalar() or 0
