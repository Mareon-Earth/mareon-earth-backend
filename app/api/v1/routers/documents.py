from fastapi import APIRouter, Depends

from app.domain.document import InitiateDocumentUploadRequest, InitiateDocumentUploadResponse
from app.domain.document.service.protocols import DocumentServiceProtocol
from app.api.v1.dependencies import get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/initiate-upload", response_model=InitiateDocumentUploadResponse)
async def get_upload_url(
    request: InitiateDocumentUploadRequest,
    svc: DocumentServiceProtocol = Depends(get_document_service),
):
    return await svc.initiate_document_upload(payload=request)