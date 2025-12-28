from fastapi import status
from app.core.exceptions.base import MareonError


class DocumentNotFoundError(MareonError):
    message = "Document not found."
    code = "DOCUMENT_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND

class DocumentFileNotFoundError(MareonError):
    message = "Document file not found."
    code = "DOCUMENT_FILE_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND

class DocumentAlreadyExistsError(MareonError):
    message = "Document already exists."
    code = "DOCUMENT_ALREADY_EXISTS"
    status_code = status.HTTP_409_CONFLICT

class DocumentFileProcessingError(MareonError):
    message = "Error processing document file."
    code = "DOCUMENT_FILE_PROCESSING_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

class InvalidDocumentFileError(MareonError):
    message = "Invalid document file."
    code = "INVALID_DOCUMENT_FILE"
    status_code = status.HTTP_400_BAD_REQUEST