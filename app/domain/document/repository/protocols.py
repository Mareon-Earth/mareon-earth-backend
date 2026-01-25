from __future__ import annotations

from abc import abstractmethod
from app.domain._shared.repository import BaseRepository
from app.domain.document.models import Document, DocumentFile

class DocumentRepositoryProtocol(BaseRepository[Document, str]):
    @abstractmethod
    async def update(self, document: Document) -> Document: ...

class DocumentFileRepositoryProtocol(BaseRepository[DocumentFile, str]):
    @abstractmethod
    async def update(self, file: DocumentFile) -> DocumentFile: ...