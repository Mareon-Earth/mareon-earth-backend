from __future__ import annotations

from abc import abstractmethod
from datetime import datetime

from app.domain._shared.repository import BaseRepository
from app.domain._shared.types import DocumentId, DocumentFileId, OrganizationId
from app.domain.document.models import Document, DocumentFile
from app.domain.document.enums import DocumentType


class DocumentRepositoryProtocol(BaseRepository[Document, DocumentId]):
    @abstractmethod
    async def update(self, document: Document) -> Document: ...

    @abstractmethod
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
    ) -> list[Document]: ...

    @abstractmethod
    async def count_by_org(
        self,
        org_id: OrganizationId,
        *,
        document_type: DocumentType | None = None,
        search: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int: ...


class DocumentFileRepositoryProtocol(BaseRepository[DocumentFile, DocumentFileId]):
    @abstractmethod
    async def update(self, file: DocumentFile) -> DocumentFile: ...

    @abstractmethod
    async def get_files_for_document(
        self,
        document_id: DocumentId,
        *,
        uploaded_only: bool = False,
    ) -> list[DocumentFile]: ...

    @abstractmethod
    async def count_files_for_document(
        self,
        document_id: DocumentId,
        *,
        uploaded_only: bool = False,
    ) -> int: ...

    @abstractmethod
    async def get_latest_file_for_document(
        self,
        document_id: DocumentId,
    ) -> DocumentFile | None: ...