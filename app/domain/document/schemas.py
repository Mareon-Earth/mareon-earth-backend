from pydantic import BaseModel
from pydantic import Field
from typing import Literal, Optional

class InitiateDocumentUploadRequest(BaseModel):
    """Request schema for upload URL generation."""
    document_id: Optional[str] = None
    mime_type: str
    original_name: str
    file_size_bytes: int

class InitiateDocumentUploadResponse(BaseModel):
    upload_url: str
    method: Literal["PUT"] = "PUT"
    required_headers: dict[str, str] = Field(default_factory=dict)
    document_id: str
    document_file_id: str
    storage_path: str