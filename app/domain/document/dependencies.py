from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.infrastructure.storage import StorageClient

from app.domain.document.service.document_service import DocumentService
from app.domain.document.service.protocols import DocumentServiceProtocol
from app.domain.document.repository import (
    DocumentRepository,
    DocumentFileRepository,
)
from app.domain.users.repository import UserRepository
from app.domain.organization.repository import OrganizationRepository


def build_document_service(
    db: AsyncSession,
    storage: StorageClient,
    ctx: AuthContext,
) -> DocumentServiceProtocol:
    doc_repo = DocumentRepository(db)
    file_repo = DocumentFileRepository(db)
    user_repo = UserRepository(db)
    org_repo = OrganizationRepository(db)

    return DocumentService(
        db=db,
        storage=storage,
        documents=doc_repo,
        files=file_repo,
        users=user_repo,
        orgs=org_repo,
        ctx=ctx,
    )