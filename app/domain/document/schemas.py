from pydantic import BaseModel
from pydantic import Field
from typing import Literal, Optional
from .enums import DocumentType

class InitiateDocumentUploadRequest(BaseModel):
    """Request schema for upload URL generation."""
    document_id: Optional[str] = None  # None = create new document
    document_title: Optional[str] = None  # Required if document_id is None
    document_type: DocumentType = DocumentType.OTHER  # Required if document_id is None

    original_name: str
    mime_type: str
    file_size_bytes: int
    content_md5_b64: str
    skip_parsing: bool = False

class InitiateDocumentUploadResponse(BaseModel):
    upload_url: str
    method: Literal["PUT"] = "PUT"
    required_headers: dict[str, str] = Field(default_factory=dict)
    document_id: str
    document_file_id: str
    storage_path: str