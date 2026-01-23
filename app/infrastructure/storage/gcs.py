from datetime import timedelta
import asyncio
from google.cloud import storage
from google.auth.exceptions import GoogleAuthError

from .protocols import StorageProtocol
from .exceptions import (
    StorageError,
    StorageFileNotFoundError,
    SignedUrlError,
    StorageDeleteError,
    StorageAuthenticationError,
)


class GCSStorage:
    """Google Cloud Storage implementation of StorageProtocol."""

    def __init__(self, bucket_name: str, project_id: str | None = None):
        """
        Initialize GCS storage client.

        Args:
            bucket_name: Name of the GCS bucket
            project_id: Optional GCP project ID
        """
        try:
            self.client = storage.Client(project=project_id)
            self.bucket = self.client.bucket(bucket_name)
            self.bucket_name = bucket_name
        except GoogleAuthError as e:
            raise StorageAuthenticationError(f"Failed to authenticate with GCS: {e}")

    async def generate_signed_url(
        self, path: str, expiration: timedelta = timedelta(hours=1)
    ) -> str:
        """Generate a signed URL for reading a file."""
        try:
            blob = self.bucket.blob(path)
            url = await asyncio.to_thread(
                blob.generate_signed_url,
                version="v4",
                expiration=expiration,
                method="GET",
            )
            return url
        except Exception as e:
            raise SignedUrlError(f"Failed to generate signed URL for {path}: {e}")

    async def generate_upload_url(
        self,
        path: str,
        content_type: str,
        expiration: timedelta = timedelta(hours=1),
    ) -> str:
        """Generate a signed URL for uploading a file."""
        try:
            blob = self.bucket.blob(path)
            url = await asyncio.to_thread(
                blob.generate_signed_url,
                version="v4",
                expiration=expiration,
                method="PUT",
                content_type=content_type,
            )
            return url
        except Exception as e:
            raise SignedUrlError(f"Failed to generate upload URL for {path}: {e}")

    async def delete_file(self, path: str) -> bool:
        """Delete a file from storage."""
        try:
            blob = self.bucket.blob(path)
            await asyncio.to_thread(blob.delete)
            return True
        except Exception as e:
            raise StorageDeleteError(f"Failed to delete file {path}: {e}")

    async def file_exists(self, path: str) -> bool:
        """Check if a file exists in storage."""
        try:
            blob = self.bucket.blob(path)
            return await asyncio.to_thread(blob.exists)
        except Exception as e:
            raise StorageError(f"Failed to check if file exists {path}: {e}")