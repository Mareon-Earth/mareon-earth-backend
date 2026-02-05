from fastapi import APIRouter, Depends, Query, status

from app.domain._shared.types import DocumentId, DocumentFileId
from app.domain.document.schemas import (
    InitiateDocumentUploadRequest,
    InitiateDocumentUploadResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentListFilters,
    DocumentUpdateRequest,
    DownloadUrlResponse,
)
from app.domain.document.service.protocols import DocumentServiceProtocol
from app.api.v1.dependencies import get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


@router.post(
    "/initiate-upload",
    response_model=InitiateDocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Initiate document upload",
    description="Create a document and/or file record and get a signed upload URL.",
)
async def initiate_upload(
    request: InitiateDocumentUploadRequest,
    svc: DocumentServiceProtocol = Depends(get_document_service),
) -> InitiateDocumentUploadResponse:
    return await svc.initiate_document_upload(payload=request)


# ---------------------------------------------------------------------------
# List / Read
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List documents",
    description="List all documents for the current organization with optional filters.",
)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    document_type: str | None = Query(None, description="Filter by document type"),
    search: str | None = Query(None, description="Search in title"),
    svc: DocumentServiceProtocol = Depends(get_document_service),
) -> DocumentListResponse:
    from app.domain.document.enums import DocumentType

    filters = DocumentListFilters(
        document_type=DocumentType(document_type) if document_type else None,
        search=search,
    )
    return await svc.list_documents(filters=filters, page=page, page_size=page_size)


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get document",
    description="Get document details including all file versions.",
)
async def get_document(
    document_id: DocumentId,
    svc: DocumentServiceProtocol = Depends(get_document_service),
) -> DocumentDetailResponse:
    return await svc.get_document(document_id=document_id)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


@router.patch(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Update document",
    description="Update document metadata (title, type, description).",
)
async def update_document(
    document_id: DocumentId,
    request: DocumentUpdateRequest,
    svc: DocumentServiceProtocol = Depends(get_document_service),
) -> DocumentDetailResponse:
    return await svc.update_document(document_id=document_id, payload=request)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete a document and all its files.",
)
async def delete_document(
    document_id: DocumentId,
    svc: DocumentServiceProtocol = Depends(get_document_service),
) -> None:
    await svc.delete_document(document_id=document_id)


@router.delete(
    "/{document_id}/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file",
    description="Delete a specific file from a document.",
)
async def delete_file(
    document_id: DocumentId,
    file_id: DocumentFileId,
    svc: DocumentServiceProtocol = Depends(get_document_service),
) -> None:
    await svc.delete_file(document_id=document_id, file_id=file_id)


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


@router.get(
    "/{document_id}/files/{file_id}/download-url",
    response_model=DownloadUrlResponse,
    summary="Get download URL",
    description="Get a signed download URL for a specific file.",
)
async def get_download_url(
    document_id: DocumentId,
    file_id: DocumentFileId,
    svc: DocumentServiceProtocol = Depends(get_document_service),
) -> DownloadUrlResponse:
    return await svc.get_download_url(document_id=document_id, file_id=file_id)


@router.get(
    "/{document_id}/download-url",
    response_model=DownloadUrlResponse,
    summary="Get latest download URL",
    description="Get a signed download URL for the latest uploaded file version.",
)
async def get_latest_download_url(
    document_id: DocumentId,
    svc: DocumentServiceProtocol = Depends(get_document_service),
) -> DownloadUrlResponse:
    return await svc.get_latest_download_url(document_id=document_id)