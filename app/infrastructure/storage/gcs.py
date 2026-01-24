from datetime import timedelta
import asyncio
from typing import cast

import google.auth
from google.cloud import storage
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError

from .exceptions import (
    StorageError,
    SignedUrlError,
    StorageDeleteError,
    StorageAuthenticationError,
)


class GCSStorage:
    """Google Cloud Storage implementation of StorageProtocol."""

    # TODO: move this to config/env (don’t hardcode)
    _SIGNER_SERVICE_ACCOUNT_EMAIL = "mareon-prod-api@mareon.iam.gserviceaccount.com"

    def __init__(self, bucket_name: str, project_id: str | None = None):
        try:
            # Get ADC creds (Cloud Run uses metadata service) + ensure proper scopes if needed
            creds, detected_project = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )  # returns google.auth.credentials.Credentials :contentReference[oaicite:6]{index=6}

            self._credentials: Credentials = cast(Credentials, creds)
            self._auth_request = Request()

            self.client = storage.Client(
                project=project_id or detected_project,
                credentials=self._credentials,
            )
            self.bucket = self.client.bucket(bucket_name)
            self.bucket_name = bucket_name

        except GoogleAuthError as e:
            raise StorageAuthenticationError(f"Failed to authenticate with GCS: {e}")

    async def _get_access_token(self) -> str:
        """
        Refresh ADC credentials (in a thread) and return the access token.
        Pylance note: Credentials.refresh(request) exists on Credentials. :contentReference[oaicite:7]{index=7}
        """
        try:
            # Refresh if needed (also covers creds.token is None)
            if not self._credentials.valid or not getattr(self._credentials, "token", None):
                await asyncio.to_thread(self._credentials.refresh, self._auth_request)

            token = getattr(self._credentials, "token", None)
            if not token:
                raise StorageAuthenticationError("GCP credentials did not provide an access token.")
            return token

        except Exception as e:
            raise StorageAuthenticationError(f"Failed to refresh GCP credentials: {e}")

    async def generate_signed_url(
        self, path: str, expiration: timedelta = timedelta(hours=1)
    ) -> str:
        try:
            blob = self.bucket.blob(path)
            access_token = await self._get_access_token()

            url = await asyncio.to_thread(
                blob.generate_signed_url,
                version="v4",
                expiration=expiration,
                method="GET",
                service_account_email=self._SIGNER_SERVICE_ACCOUNT_EMAIL,
                access_token=access_token,
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
        try:
            blob = self.bucket.blob(path)
            access_token = await self._get_access_token()

            url = await asyncio.to_thread(
                blob.generate_signed_url,
                version="v4",
                expiration=expiration,
                method="PUT",
                content_type=content_type,
                service_account_email=self._SIGNER_SERVICE_ACCOUNT_EMAIL,
                access_token=access_token,
            )
            return url

        except Exception as e:
            raise SignedUrlError(f"Failed to generate upload URL for {path}: {e}")

    async def delete_file(self, path: str) -> bool:
        try:
            blob = self.bucket.blob(path)
            await asyncio.to_thread(blob.delete)
            return True
        except Exception as e:
            raise StorageDeleteError(f"Failed to delete file {path}: {e}")

    async def file_exists(self, path: str) -> bool:
        try:
            blob = self.bucket.blob(path)
            return await asyncio.to_thread(blob.exists)
        except Exception as e:
            raise StorageError(f"Failed to check if file exists {path}: {e}")
