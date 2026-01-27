from app.domain.document.models import (
    Document,
    DocumentFile,
)
from app.domain.document.enums import (
    DocumentType,
    DocumentContentType,
    ProcessingStatus,
)
from app.domain.document.repository import (
    DocumentRepository,
    DocumentFileRepository,
    DocumentRepositoryProtocol,
    DocumentFileRepositoryProtocol,
)
from app.domain.document.service import DocumentServiceProtocol
from app.domain.document.exceptions import (
    DocumentNotFoundError,
    DocumentFileNotFoundError,
    DocumentAlreadyExistsError,
    DocumentFileProcessingError,
    InvalidDocumentFileError,
)
from app.domain.document.schemas import (
    InitiateDocumentUploadRequest,
    InitiateDocumentUploadResponse,
)

__all__ = [
    # Models
    "Document",
    "DocumentFile",
    # Repo protocols
    "DocumentRepositoryProtocol",
    "DocumentFileRepositoryProtocol",
    # Service protocol
    "DocumentServiceProtocol",
    # Enums
    "DocumentType",
    "DocumentContentType",
    "ProcessingStatus",
    # Repository impls
    "DocumentRepository",
    "DocumentFileRepository",
    # Exceptions
    "DocumentNotFoundError",
    "DocumentFileNotFoundError",
    "DocumentAlreadyExistsError",
    "DocumentFileProcessingError",
    "InvalidDocumentFileError",
    # Schemas
    "InitiateDocumentUploadRequest",
    "InitiateDocumentUploadResponse",
]
