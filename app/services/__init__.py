from fastapi import Depends

from app.core.auth import AuthContext, get_auth_context
from app.domain.document import DocumentRepository
from app.domain.protocols.repositories import DocumentRepositoryProtocol
from app.infrastructure.storage import StorageClient, get_storage_client
from app.services.document_service import DocumentService


def get_document_repository() -> DocumentRepositoryProtocol:
    return DocumentRepository()


def get_document_service(
    storage: StorageClient = Depends(get_storage_client),
    repo: DocumentRepositoryProtocol = Depends(get_document_repository),
    ctx: AuthContext = Depends(get_auth_context),
) -> DocumentService:
    return DocumentService(storage=storage, repo=repo, ctx=ctx)
