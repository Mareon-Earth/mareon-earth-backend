from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext, get_auth_context
from app.infrastructure.db import get_db_session
from app.infrastructure.storage import StorageClient, get_storage_client
from app.domain.document.service.protocols import DocumentServiceProtocol
from app.domain.document.dependencies import build_document_service

def get_document_service(
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
    storage: StorageClient = Depends(get_storage_client),
) -> DocumentServiceProtocol:
    return build_document_service(db=db, storage=storage, ctx=ctx)