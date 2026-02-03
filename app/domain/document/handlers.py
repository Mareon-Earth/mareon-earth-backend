from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pubsub import (
    GcsObjectMetadata,
    GcsUploadHandler,
    PubSubContext,
    PubSubDropError,
    PubSubRetryableError,
    PubSubSubscription,
)
from app.domain.processing.enums import ParsingJobStatus
from app.domain.processing.models import ParsingJob
from app.domain.processing.repository import ParsingJobRepository
from app.domain.document.repository import DocumentFileRepository

if TYPE_CHECKING:
    from app.infrastructure.db.session_manager import SessionManager

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ParsedUploadPath:
    org_id: str
    document_id: str
    document_file_id: str
    filename: str

    @classmethod
    def from_gcs_path(cls, path: str) -> "ParsedUploadPath | None":
        pattern = r"^org-uploads/([^/]+)/documents/([^/]+)/files/([^/]+)/(.+)$"
        match = re.match(pattern, path)
        if not match:
            return None

        return cls(
            org_id=match.group(1),
            document_id=match.group(2),
            document_file_id=match.group(3),
            filename=match.group(4),
        )

class DocumentUploadHandler(GcsUploadHandler):
    name = "document_upload_handler"
    subscriptions = {PubSubSubscription.DOCUMENT_UPLOADS_API}
    allowed_prefixes = {"org-uploads/"}

    allowed_content_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/png",
        "image/jpeg",
    }

    def __init__(self, session_manager: "SessionManager") -> None:
        self._session_manager = session_manager

    async def handle_upload(self, ctx: PubSubContext, metadata: GcsObjectMetadata) -> None:
        logger.info("Processing upload: %s", metadata.name)

        parsed = ParsedUploadPath.from_gcs_path(metadata.name)
        if not parsed:
            raise PubSubDropError(f"Invalid path: {metadata.name}")

        async with self._session_manager() as session:
            try:
                await self._process_upload(session, ctx, metadata, parsed)
                await session.commit()
            except (PubSubDropError, PubSubRetryableError):
                await session.rollback()
                raise
            except Exception as e:
                await session.rollback()
                logger.exception("Error processing upload: %s", metadata.name)
                raise PubSubRetryableError(f"Unexpected error: {e}") from e

    async def _process_upload(
        self,
        session: AsyncSession,
        ctx: PubSubContext,
        metadata: GcsObjectMetadata,
        parsed: ParsedUploadPath,
    ) -> None:
        file_repo = DocumentFileRepository(session)
        job_repo = ParsingJobRepository(session)

        doc_file = await file_repo.get_by_id(parsed.document_file_id)
        if not doc_file:
            raise PubSubDropError(f"DocumentFile not found: {parsed.document_file_id}")

        if str(doc_file.org_id) != parsed.org_id:
            raise PubSubDropError("Org ID mismatch")

        requires_parsing = getattr(doc_file, 'requires_parsing', True)
        if not requires_parsing:
            return

        if await job_repo.does_job_exist_for_file(parsed.document_file_id):
            return

        if ctx.message_id and await job_repo.does_job_exist_for_message(ctx.message_id):
            return

        parsing_job = ParsingJob(
            org_id=parsed.org_id,
            document_id=parsed.document_id,
            document_file_id=parsed.document_file_id,
            status=ParsingJobStatus.PENDING,
            attempt_count=0,
            pubsub_message_id=ctx.message_id,
            pubsub_publish_time=ctx.publish_time,
            source_gcs_object=f"gs://{metadata.bucket}/{metadata.name}",
            result_gcs_bucket=metadata.bucket,
            result_gcs_prefix=f"org-uploads/{parsed.org_id}/documents/{parsed.document_id}/files/{parsed.document_file_id}/parsing/",
        )

        await job_repo.create(parsing_job)
        logger.info("Created ParsingJob %s", parsing_job.id)