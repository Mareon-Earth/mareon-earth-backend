from typing import Protocol

from app.domain._shared.types import DocumentId, DocumentFileId
from app.domain.document.schemas import (
    InitiateDocumentUploadRequest,
    InitiateDocumentUploadResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentListFilters,
    DocumentUpdateRequest,
    DownloadUrlResponse,
    DocumentSummary,
)


class DocumentServiceProtocol(Protocol):
    # Upload
    async def initiate_document_upload(
        self, payload: InitiateDocumentUploadRequest
    ) -> InitiateDocumentUploadResponse: ...

    # Read
    async def get_document(self, document_id: DocumentId) -> DocumentDetailResponse: ...

    async def list_documents(
        self,
        filters: DocumentListFilters | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> DocumentListResponse: ...

    # Update
    async def update_document(
        self, document_id: DocumentId, payload: DocumentUpdateRequest
    ) -> DocumentDetailResponse: ...

    # Delete
    async def delete_document(self, document_id: DocumentId) -> None: ...

    async def delete_file(self, document_id: DocumentId, file_id: DocumentFileId) -> None: ...

    # Download
    async def get_download_url(
        self, document_id: DocumentId, file_id: DocumentFileId
    ) -> DownloadUrlResponse: ...

    async def get_latest_download_url(
        self, document_id: DocumentId
    ) -> DownloadUrlResponse: ...
