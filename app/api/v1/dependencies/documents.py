from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext, get_auth_context
from app.infrastructure.db import get_db_session
from app.infrastructure.storage import StorageClient, get_storage_client

from app.domain.document.service.protocols import DocumentServiceProtocol
from app.domain.document.service.document_service import DocumentService

from app.domain.document.repository.document_repository import DocumentRepository
from app.domain.document.repository.file_repository import DocumentFileRepository
from app.domain.users.repository import UserRepository
from app.domain.organization.repository import OrganizationRepository



def get_document_service(
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
    storage: StorageClient = Depends(get_storage_client),
) -> DocumentServiceProtocol:
    doc_repo = DocumentRepository(db)
    file_repo = DocumentFileRepository(db)
    user_repo = UserRepository(db)
    org_repo = OrganizationRepository(db)

    return DocumentService(
        db=db,
        ctx=ctx,
        storage=storage,
        documents=doc_repo,
        files=file_repo,
        users=user_repo,
        orgs=org_repo,
    )