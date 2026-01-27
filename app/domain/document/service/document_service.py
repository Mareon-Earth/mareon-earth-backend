from __future__ import annotations

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
from app.domain.document.repository import (
    DocumentRepositoryProtocol,
    DocumentFileRepositoryProtocol,
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

    async def initiate_document_upload(
        self, payload: InitiateDocumentUploadRequest
    ) -> InitiateDocumentUploadResponse:
        """
        Creates (or validates) a Document, creates a DocumentFile row,
        assigns deterministic storage_path, returns a signed upload URL.
        """
        try:
            # Prefer internal IDs from Clerk metadata when available (saves DB hits)
            org_id = self._ctx.internal_org_id
            if not org_id:
                org = await self._orgs.get_by_clerk_id(
                    db=self._db,
                    clerk_id=self._ctx.organization_id,
                )
                if not org:
                    # TODO: replace with an org-specific error once DomainError handler exists
                    raise DocumentNotFoundError()
                org_id = org.id

            user_id = self._ctx.internal_user_id
            if not user_id:
                user = await self._users.get_by_clerk_id(
                    clerk_user_id=self._ctx.user_id,
                )
                if not user:
                    # TODO: replace with a user-specific error once DomainError handler exists
                    raise DocumentNotFoundError()
                user_id = user.id

            # 1) Use existing doc or create a new one
            if payload.document_id:
                doc = await self._documents.get_by_id(payload.document_id)
                if not doc or doc.org_id != org_id:
                    raise DocumentNotFoundError()
            else:
                doc = Document(
                    org_id=org_id,
                    created_by=user_id,
                    title="Untitled Document",
                    document_type=DocumentType.OTHER,
                )
                await self._documents.create(doc)

            document_id = doc.id

            # 2) Create file row (need flush to get file id for storage_path)
            doc_file = DocumentFile(
                document_id=document_id,
                org_id=org_id,
                storage_path="pending",  # placeholder until we can compute deterministic path
                original_name=payload.original_name,
                mime_type=payload.mime_type,
                file_size_bytes=payload.file_size_bytes,
                uploaded_by=user_id,
            )
            await self._files.create(doc_file)

            document_file_id = doc_file.id
            storage_path = f"org/{org_id}/documents/{document_id}/files/{document_file_id}"

            doc_file.storage_path = storage_path
            await self._files.update(doc_file)

            # 3) Signed upload URL
            content_type = payload.mime_type or "application/octet-stream"
            upload_url = await self._storage.generate_upload_url(
                path=storage_path,
                content_type=content_type,
                expiration=timedelta(hours=1),
            )

            await self._db.commit()

            return InitiateDocumentUploadResponse(
                upload_url=upload_url,
                method="PUT",
                required_headers={"Content-Type": content_type},
                document_id=document_id,
                document_file_id=document_file_id,
                storage_path=storage_path,
            )

        except Exception:
            await self._db.rollback()
            raise
