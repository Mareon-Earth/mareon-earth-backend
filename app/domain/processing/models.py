from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import UUIDPrimaryKeyMixin, TimestampsMixin

# FIX 1: Import Enum here (runtime), not inside TYPE_CHECKING
from .enums import ParsingJobStatus

if TYPE_CHECKING:
    from app.domain.organization import Organization
    from app.domain.document import Document, DocumentFile


class ParsingJob(UUIDPrimaryKeyMixin, TimestampsMixin, Base):
    __tablename__ = "parsing_job"

    org_id: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_id: sa.Mapped[str | None] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    document_file_id: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("document_file.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: sa.Mapped[ParsingJobStatus] = sa.mapped_column(
        sa.SAEnum(ParsingJobStatus, name="parsing_job_status", native_enum=False),
        nullable=False,
        server_default=sa.text(f"'{ParsingJobStatus.PENDING.value}'"),
        index=True,
    )

    attempt_count: sa.Mapped[int] = sa.mapped_column(
        sa.Integer,
        nullable=False,
        server_default=sa.text("0"),
    )

    max_attempts: sa.Mapped[int] = sa.mapped_column(
        sa.Integer,
        nullable=False,
        server_default=sa.text("2"),
    )

    started_at: sa.Mapped[sa.DateTime | None] = sa.mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    finished_at: sa.Mapped[sa.DateTime | None] = sa.mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )

    duration_ms: sa.Mapped[int | None] = sa.mapped_column(sa.BigInteger, nullable=True)

    error_message: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)
    error_details: sa.Mapped[dict | None] = sa.mapped_column(sa.JSONB, nullable=True)

    # Pub/Sub related (debugging + idempotency)
    pubsub_message_id: sa.Mapped[str | None] = sa.mapped_column(sa.String, nullable=True, index=True)
    pubsub_publish_time: sa.Mapped[sa.DateTime | None] = sa.mapped_column(sa.DateTime(timezone=True), nullable=True)

    # Storage paths
    result_gcs_bucket: sa.Mapped[str | None] = sa.mapped_column(sa.String, nullable=True)
    result_gcs_prefix: sa.Mapped[str | None] = sa.mapped_column(sa.String, nullable=True)
    source_gcs_object: sa.Mapped[str | None] = sa.mapped_column(sa.String, nullable=True)

    __table_args__ = (
        # 1. One active job per file (Partial Index)
        sa.Index(
            "ux_parsing_job_active_file",
            "document_file_id",
            unique=True,
            postgresql_where=sa.text(
                "status IN ('PENDING','QUEUED','PROCESSING','RETRYING')"
            ),
        ),
        
        # FIX 2: Changed from UniqueConstraint to Index(unique=True)
        # because UniqueConstraint does not support 'postgresql_where'
        sa.Index(
            "uq_parsing_job_pubsub_message_id",
            "pubsub_message_id",
            unique=True,
            postgresql_where=sa.text("pubsub_message_id IS NOT NULL"),
        ),

        # Helpful indexes
        sa.Index("ix_parsing_job_document_file_status", "document_file_id", "status"),
        sa.Index("ix_parsing_job_org_status_created", "org_id", "status", "created_at"),
        sa.Index("ix_parsing_job_status_created_at", "status", "created_at"),
    )

    organization: sa.Mapped["Organization"] = sa.relationship("Organization", foreign_keys=[org_id])
    document: sa.Mapped["Document"] = sa.relationship("Document", foreign_keys=[document_id])
    document_file: sa.Mapped["DocumentFile"] = sa.relationship("DocumentFile", foreign_keys=[document_file_id])

__all__ = [
    "ParsingJob"
]