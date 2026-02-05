from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import DocumentId, DocumentFileId
from app.domain.document.models import DocumentFile
from app.domain.document.repository.protocols import DocumentFileRepositoryProtocol


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
        doc_file = await self.get_by_id(id)
        if doc_file is not None:
            await self._db.delete(doc_file)
            await self._db.flush()

    async def update(self, file: DocumentFile) -> DocumentFile:
        await self._db.flush()
        return file

    async def get_files_for_document(
        self,
        document_id: DocumentId,
        *,
        uploaded_only: bool = False,
    ) -> list[DocumentFile]:
        filters = [DocumentFile.document_id == document_id]

        if uploaded_only:
            filters.append(DocumentFile.source_uri.isnot(None))

        stmt = (
            select(DocumentFile)
            .where(*filters)
            .order_by(DocumentFile.version_number.desc())
        )

        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def count_files_for_document(
        self,
        document_id: DocumentId,
        *,
        uploaded_only: bool = False,
    ) -> int:
        filters = [DocumentFile.document_id == document_id]

        if uploaded_only:
            filters.append(DocumentFile.source_uri.isnot(None))

        stmt = select(func.count()).select_from(DocumentFile).where(*filters)
        result = await self._db.execute(stmt)
        return result.scalar() or 0

    async def get_latest_file_for_document(
        self,
        document_id: DocumentId,
    ) -> DocumentFile | None:
        stmt = (
            select(DocumentFile)
            .where(
                DocumentFile.document_id == document_id,
                DocumentFile.is_latest == True,  # noqa: E712
                DocumentFile.source_uri.isnot(None),
            )
            .limit(1)
        )

        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()
