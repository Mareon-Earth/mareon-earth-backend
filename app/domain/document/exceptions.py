from app.domain._shared.errors import Conflict, NotFound, DomainError


class DocumentNotFoundError(NotFound):
    code = "DOCUMENT_NOT_FOUND"
    message = "Document not found."


class DocumentFileNotFoundError(NotFound):
    code = "DOCUMENT_FILE_NOT_FOUND"
    message = "Document file not found."


class DocumentAlreadyExistsError(Conflict):
    code = "DOCUMENT_ALREADY_EXISTS"
    message = "Document already exists."


class DocumentFileProcessingError(DomainError):
    code = "DOCUMENT_FILE_PROCESSING_ERROR"
    message = "Error processing document file."


class InvalidDocumentFileError(DomainError):
    code = "INVALID_DOCUMENT_FILE"
    message = "Invalid document file."
