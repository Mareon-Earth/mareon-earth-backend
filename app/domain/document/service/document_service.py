from __future__ import annotations

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.domain._shared.types import DocumentId, DocumentFileId
from app.domain.document.enums import DocumentType
from app.domain.document.exceptions import (
    DocumentNotFoundError,
    DocumentFileNotFoundError,
)
from app.domain.document.models import Document, DocumentFile
from app.domain.document.repository.protocols import (
    DocumentRepositoryProtocol,
    DocumentFileRepositoryProtocol,
)
from app.domain.document.schemas import (
    InitiateDocumentUploadRequest,
    InitiateDocumentUploadResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentListFilters,
    DocumentUpdateRequest,
    DownloadUrlResponse,
    DocumentSummary,
    DocumentFileResponse,
)
from app.domain.document.service.protocols import DocumentServiceProtocol
from app.domain.users.repository.protocols import UserRepositoryProtocol
from app.domain.organization.repository.protocols import OrganizationRepositoryProtocol
from app.infrastructure.storage import StorageClient


class DocumentService(DocumentServiceProtocol):
    """
    Application service for document flows.

    Note:
    - This service is request-scoped (it holds an AsyncSession).
    - Routers should be thin wrappers: `return await svc.method(payload)`
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        storage: StorageClient,
        documents: DocumentRepositoryProtocol,
        files: DocumentFileRepositoryProtocol,
        users: UserRepositoryProtocol,
        orgs: OrganizationRepositoryProtocol,
        ctx: AuthContext,
    ):
        self._db = db
        self._storage = storage
        self._documents = documents
        self._files = files
        self._users = users
        self._orgs = orgs
        self._ctx = ctx

    # ---------------------------------------------------------------------------
    # Upload
    # ---------------------------------------------------------------------------

    async def initiate_document_upload(
        self, payload: InitiateDocumentUploadRequest
    ) -> InitiateDocumentUploadResponse:
        """
        Creates (or validates) a Document, creates a DocumentFile row with source_uri=None,
        returns a signed upload URL. source_uri will be set when upload is confirmed via Pub/Sub.
        """
        try:
            org_id = self._ctx.internal_org_id
            user_id = self._ctx.internal_user_id

            # 1) Use existing doc or create a new one
            if payload.document_id:
                doc = await self._documents.get_by_id(payload.document_id)
                if not doc or doc.org_id != org_id:
                    raise DocumentNotFoundError()
            else:
                doc = Document(
                    org_id=org_id,
                    title=payload.document_title or "Untitled Document",
                    document_type=payload.document_type or DocumentType.OTHER,
                    created_by=user_id,
                )
                await self._documents.create(doc)

            document_id = doc.id

            # 2) Create file row with source_uri=None (will be set on upload confirmation)
            doc_file = DocumentFile(
                document_id=document_id,
                org_id=org_id,
                source_uri=None,  # Set by Pub/Sub handler when upload completes
                original_name=payload.original_name or "Untitled",
                mime_type=payload.mime_type or "application/octet-stream",
                file_size_bytes=payload.file_size_bytes,
                content_md5_b64=payload.content_md5_b64 or None,
                uploaded_by=user_id,
                requires_parsing=not payload.skip_parsing,
            )
            await self._files.create(doc_file)

            document_file_id = doc_file.id

            # 3) Compute expected GCS path for signed URL (not stored in DB yet)
            expected_path = (
                f"org-uploads/{org_id}/documents/{document_id}/files/{document_file_id}/source"
            )

            # 4) Signed upload URL
            content_type = payload.mime_type or "application/octet-stream"
            upload_url = await self._storage.generate_upload_url(
                path=expected_path,
                content_type=content_type,
                content_md5=payload.content_md5_b64,
                expiration=timedelta(hours=1),
            )

            await self._db.commit()

            return InitiateDocumentUploadResponse(
                upload_url=upload_url,
                method="PUT",
                required_headers={
                    "Content-Type": content_type,
                    "Content-MD5": payload.content_md5_b64,
                },
                document_id=document_id,
                document_file_id=document_file_id,
                expected_path=expected_path,
            )

        except Exception:
            await self._db.rollback()
            raise

    # ---------------------------------------------------------------------------
    # Read
    # ---------------------------------------------------------------------------

    async def get_document(self, document_id: DocumentId) -> DocumentDetailResponse:
        """Get document details with all files."""
        org_id = self._ctx.internal_org_id

        doc = await self._documents.get_by_id(document_id)
        if not doc or doc.org_id != org_id:
            raise DocumentNotFoundError()

        files = await self._files.get_files_for_document(document_id)

        return DocumentDetailResponse(
            id=doc.id,
            title=doc.title,
            document_type=doc.document_type,
            description=doc.description,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            created_by=doc.created_by,
            files=[
                DocumentFileResponse(
                    id=f.id,
                    original_name=f.original_name,
                    mime_type=f.mime_type,
                    file_size_bytes=f.file_size_bytes,
                    version_number=f.version_number,
                    is_latest=f.is_latest,
                    is_uploaded=f.is_uploaded,
                    uploaded_at=f.uploaded_at,
                    uploaded_by=f.uploaded_by,
                    requires_parsing=f.requires_parsing,
                    source_uri=f.source_uri,
                )
                for f in files
            ],
        )

    async def list_documents(
        self,
        filters: DocumentListFilters | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> DocumentListResponse:
        """List documents for the current org with optional filters."""
        org_id = self._ctx.internal_org_id
        filters = filters or DocumentListFilters()

        offset = (page - 1) * page_size

        documents = await self._documents.list_by_org(
            org_id,
            document_type=filters.document_type,
            search=filters.search,
            created_after=filters.created_after,
            created_before=filters.created_before,
            offset=offset,
            limit=page_size,
        )

        total = await self._documents.count_by_org(
            org_id,
            document_type=filters.document_type,
            search=filters.search,
            created_after=filters.created_after,
            created_before=filters.created_before,
        )

        # Single query to get all file counts — avoids N+1
        doc_ids = [doc.id for doc in documents]
        counts = await self._files.count_files_bulk(doc_ids)

        items: list[DocumentSummary] = []
        for doc in documents:
            file_count, uploaded_file_count = counts.get(doc.id, (0, 0))
            items.append(
                DocumentSummary(
                    id=doc.id,
                    title=doc.title,
                    document_type=doc.document_type,
                    description=doc.description,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at,
                    created_by=doc.created_by,
                    file_count=file_count,
                    uploaded_file_count=uploaded_file_count,
                )
            )

        return DocumentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    # ---------------------------------------------------------------------------
    # Update
    # ---------------------------------------------------------------------------

    async def update_document(
        self, document_id: DocumentId, payload: DocumentUpdateRequest
    ) -> DocumentDetailResponse:
        """Update document metadata."""
        org_id = self._ctx.internal_org_id

        doc = await self._documents.get_by_id(document_id)
        if not doc or doc.org_id != org_id:
            raise DocumentNotFoundError()

        if payload.title is not None:
            doc.title = payload.title
        if payload.document_type is not None:
            doc.document_type = payload.document_type
        if payload.description is not None:
            doc.description = payload.description

        await self._documents.update(doc)
        await self._db.commit()

        return await self.get_document(document_id)

    # ---------------------------------------------------------------------------
    # Delete
    # ---------------------------------------------------------------------------

    async def delete_document(self, document_id: DocumentId) -> None:
        """Delete a document and all its files."""
        org_id = self._ctx.internal_org_id

        doc = await self._documents.get_by_id(document_id)
        if not doc or doc.org_id != org_id:
            raise DocumentNotFoundError()

        # TODO: Optionally delete files from GCS as well
        await self._documents.delete(document_id)
        await self._db.commit()

    async def delete_file(self, document_id: DocumentId, file_id: DocumentFileId) -> None:
        """Delete a specific file from a document."""
        org_id = self._ctx.internal_org_id

        doc = await self._documents.get_by_id(document_id)
        if not doc or doc.org_id != org_id:
            raise DocumentNotFoundError()

        doc_file = await self._files.get_by_id(file_id)
        if not doc_file or doc_file.document_id != document_id:
            raise DocumentFileNotFoundError()

        # TODO: Optionally delete file from GCS as well
        await self._files.delete(file_id)
        await self._db.commit()

    # ---------------------------------------------------------------------------
    # Download
    # ---------------------------------------------------------------------------

    async def get_download_url(
        self, document_id: DocumentId, file_id: DocumentFileId
    ) -> DownloadUrlResponse:
        """Generate a signed download URL for a specific file."""
        org_id = self._ctx.internal_org_id

        doc = await self._documents.get_by_id(document_id)
        if not doc or doc.org_id != org_id:
            raise DocumentNotFoundError()

        doc_file = await self._files.get_by_id(file_id)
        if not doc_file or doc_file.document_id != document_id:
            raise DocumentFileNotFoundError()

        if not doc_file.source_uri:
            raise DocumentFileNotFoundError(
                message="File has not been uploaded yet."
            )

        expiration = timedelta(hours=1)
        download_url = await self._storage.generate_download_url(
            path=doc_file.source_uri,
            expiration=expiration,
            filename=doc_file.original_name,
        )

        return DownloadUrlResponse(
            download_url=download_url,
            expires_in_seconds=int(expiration.total_seconds()),
            filename=doc_file.original_name or "download",
            content_type=doc_file.mime_type,
            file_size_bytes=doc_file.file_size_bytes,
        )

    async def get_latest_download_url(self, document_id: DocumentId) -> DownloadUrlResponse:
        """Generate a signed download URL for the latest file version."""
        org_id = self._ctx.internal_org_id

        doc = await self._documents.get_by_id(document_id)
        if not doc or doc.org_id != org_id:
            raise DocumentNotFoundError()

        doc_file = await self._files.get_latest_file_for_document(document_id)
        if not doc_file:
            raise DocumentFileNotFoundError(
                message="No uploaded files found for this document."
            )

        return await self.get_download_url(document_id, doc_file.id)
