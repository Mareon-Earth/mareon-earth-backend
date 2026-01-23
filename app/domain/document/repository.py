from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.domain.protocols.repositories import (
    DocumentRepositoryProtocol,
)

from app.domain.document.models import Document, DocumentFile

class DocumentRepository(DocumentRepositoryProtocol):
    async def getDocumentById(self, db: AsyncSession, document_id: str) -> Optional["Document"]:
        stmt = select(Document).where(Document.id == document_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def createDocument(self, db: AsyncSession, document: "Document") -> "Document":
        db.add(document)
        await db.flush()
        return document

    async def updateDocument(self, db: AsyncSession, document: "Document") -> "Document":
        await db.flush()
        return document

    async def deleteDocument(self, db: AsyncSession, document: "Document") -> None:
        await db.delete(document)
        await db.flush()

    async def getDocumentFileById(self, db: AsyncSession, document_file_id: str) -> Optional["DocumentFile"]:
        stmt = select(DocumentFile).where(DocumentFile.id == document_file_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def createDocumentFile(self, db: AsyncSession, document_file: "DocumentFile") -> "DocumentFile":
        db.add(document_file)
        await db.flush()
        return document_file

    async def updateDocumentFile(self, db: AsyncSession, document_file: "DocumentFile") -> "DocumentFile":
        await db.flush()
        return document_file
    
    async def deleteDocumentFile(self, db: AsyncSession, document_file: "DocumentFile") -> None:
        await db.delete(document_file)
        await db.flush()