from __future__ import annotations

from app.domain._shared.types import DateTime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

from app.domain._shared.schemas import RequestSchema, ResponseSchema, PaginatedResponse
from .enums import DocumentType


# ---------------------------------------------------------------------------
# Upload Initiation
# ---------------------------------------------------------------------------


class InitiateDocumentUploadRequest(RequestSchema):
    """Request schema for upload URL generation."""

    document_id: str | None = None  # None = create new document
    document_title: str | None = None  # Required if document_id is None
    document_type: DocumentType = DocumentType.OTHER

    original_name: str
    mime_type: str
    file_size_bytes: int
    content_md5_b64: str
    skip_parsing: bool = False


class InitiateDocumentUploadResponse(ResponseSchema):
    """Response with signed upload URL and file identifiers."""

    upload_url: str
    method: Literal["PUT"] = "PUT"
    required_headers: dict[str, str] = Field(default_factory=dict)
    document_id: str
    document_file_id: str
    # The expected GCS path (for client reference). source_uri will be set on upload confirmation.
    expected_path: str


# ---------------------------------------------------------------------------
# Document File Responses
# ---------------------------------------------------------------------------


class DocumentFileResponse(ResponseSchema):
    """File details for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    original_name: str | None
    mime_type: str | None
    file_size_bytes: int | None
    version_number: int
    is_latest: bool
    is_uploaded: bool
    uploaded_at: DateTime
    uploaded_by: str | None
    requires_parsing: bool
    source_uri: str | None = None


# ---------------------------------------------------------------------------
# Document Responses
# ---------------------------------------------------------------------------


class DocumentSummary(ResponseSchema):
    """Summary view for document listings."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    document_type: DocumentType
    description: str | None
    created_at: DateTime
    updated_at: DateTime
    created_by: str
    file_count: int = 0
    uploaded_file_count: int = 0


class DocumentDetailResponse(ResponseSchema):
    """Full document details with files."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    document_type: DocumentType
    description: str | None
    created_at: DateTime
    updated_at: DateTime
    created_by: str
    files: list[DocumentFileResponse] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Document List / Filter
# ---------------------------------------------------------------------------


class DocumentListFilters(RequestSchema):
    """Query filters for document listing."""

    document_type: DocumentType | None = None
    search: str | None = None  # title search
    created_after: DateTime | None = None
    created_before: DateTime | None = None
    has_pending_uploads: bool | None = None


class DocumentListResponse(PaginatedResponse[DocumentSummary]):
    """Paginated document list."""

    pass


# ---------------------------------------------------------------------------
# Document Update
# ---------------------------------------------------------------------------


class DocumentUpdateRequest(RequestSchema):
    """Request to update document metadata."""

    title: str | None = None
    document_type: DocumentType | None = None
    description: str | None = None


# ---------------------------------------------------------------------------
# Download URL
# ---------------------------------------------------------------------------


class DownloadUrlResponse(ResponseSchema):
    """Signed download URL response."""

    download_url: str
    expires_in_seconds: int
    filename: str
    content_type: str | None
    file_size_bytes: int | None