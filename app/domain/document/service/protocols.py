from typing import Protocol

from app.domain.document.schemas import (
    InitiateDocumentUploadRequest,
    InitiateDocumentUploadResponse,
)


class DocumentServiceProtocol(Protocol):
    async def initiate_document_upload(
        self, payload: InitiateDocumentUploadRequest
    ) -> InitiateDocumentUploadResponse: ...
