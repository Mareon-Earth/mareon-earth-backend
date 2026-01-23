from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.domain.document import (
    Document,
    DocumentFile,
    DocumentType,
    InitiateDocumentUploadRequest,
    InitiateDocumentUploadResponse,
    DocumentNotFoundError,
)
from app.domain.protocols.repositories import DocumentRepositoryProtocol
from app.domain.protocols.services import DocumentServiceProtocol
from app.infrastructure.storage import StorageClient


class DocumentService(DocumentServiceProtocol):
    def __init__(
        self,
        *,
        storage: StorageClient,
        repo: DocumentRepositoryProtocol,
        ctx: AuthContext,
    ):
        self._storage = storage
        self._repo = repo
        self._ctx = ctx

    async def initiate_document_upload(
        self,
        db: AsyncSession,
        payload: InitiateDocumentUploadRequest,
    ) -> InitiateDocumentUploadResponse:
        org_id = self._ctx.organization_id
        user_id = self._ctx.user_id

        if payload.document_id:
            doc = await self._repo.getDocumentById(db=db, document_id=payload.document_id)
            if not doc or doc.org_id != org_id:
                raise DocumentNotFoundError()
        else:
            doc = Document(
                org_id=org_id,
                created_by=user_id,
                title="Untitled Document",
                document_type=DocumentType.OTHER,
            )
            await self._repo.createDocument(db=db, document=doc)

        document_id = doc.id

        doc_file = DocumentFile(
            document_id=document_id,
            org_id=org_id,
            storage_path="",
            original_name=payload.original_name,
            mime_type=payload.mime_type,
            file_size_bytes=payload.file_size_bytes,
            uploaded_by=user_id,
        )
        await self._repo.createDocumentFile(db=db, document_file=doc_file)

        document_file_id = doc_file.id
        storage_path = f"org/{org_id}/documents/{document_id}/files/{document_file_id}"

        doc_file.storage_path = storage_path
        await self._repo.updateDocumentFile(db=db, document_file=doc_file)

        content_type = payload.mime_type or "application/octet-stream"
        upload_url = await self._storage.generate_upload_url(
            path=storage_path,
            content_type=content_type,
            expiration=timedelta(hours=1),
        )

        await db.commit()

        return InitiateDocumentUploadResponse(
            upload_url=upload_url,
            method="PUT",
            required_headers={"Content-Type": content_type},
            document_id=document_id,
            document_file_id=document_file_id,
            storage_path=storage_path,
        )
