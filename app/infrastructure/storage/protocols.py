from typing import Protocol, Union
from datetime import timedelta


class StorageProtocol(Protocol):
    """Protocol defining the interface for cloud storage operations."""

    async def generate_download_url(
        self,
        path: str,
        expiration: timedelta = timedelta(hours=1),
        filename: str | None = None,
    ) -> str:
        """Generate a signed URL for reading a file."""
        ...
        
    async def generate_upload_url(
        self,
        path: str,
        content_type: str,
        content_md5: str | None,
        expiration: timedelta = timedelta(hours=1),
    ) -> str:
        """Generate a signed URL for uploading a file."""
        ...

    async def delete_file(self, path: str) -> bool:
        """Delete a file from storage."""
        ...

    async def file_exists(self, path: str) -> bool:
        """Check if a file exists in storage."""
        ...
