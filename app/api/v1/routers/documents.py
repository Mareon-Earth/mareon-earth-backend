from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import AuthContext, get_auth_context

from app.infrastructure.db import get_db_session
from app.domain.document import (InitiateDocumentUploadRequest, InitiateDocumentUploadResponse)
from app.domain.protocols.services import DocumentServiceProtocol
from app.services import get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/initiate-upload", response_model=InitiateDocumentUploadResponse)
async def get_upload_url(
    request: InitiateDocumentUploadRequest,
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
    svc: DocumentServiceProtocol = Depends(get_document_service),
):
    return await svc.initiate_document_upload(db=db, payload=request)