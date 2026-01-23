from fastapi import status
from app.core.exceptions.base import MareonError


class StorageError(MareonError):
    """Base exception for storage operations."""
    message = "Storage operation failed."
    code = "STORAGE_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class StorageFileNotFoundError(MareonError):
    """Raised when a file is not found in storage."""
    message = "File not found in storage."
    code = "STORAGE_FILE_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class SignedUrlError(MareonError):
    """Raised when signed URL generation fails."""
    message = "Failed to generate signed URL."
    code = "SIGNED_URL_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class StorageDeleteError(MareonError):
    """Raised when file deletion fails."""
    message = "Failed to delete file from storage."
    code = "STORAGE_DELETE_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class StorageAuthenticationError(MareonError):
    """Raised when storage authentication fails."""
    message = "Storage authentication failed."
    code = "STORAGE_AUTHENTICATION_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR