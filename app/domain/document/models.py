from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import UUIDPrimaryKeyMixin, TimestampsMixin

from .enums import DocumentType, ParsingStatus

if TYPE_CHECKING:
    from app.domain.organization.models import Organization
    from app.domain.users.models import User


class Document(UUIDPrimaryKeyMixin, TimestampsMixin, Base):
    __tablename__ = "document"

    org_id: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: sa.Mapped[str] = sa.mapped_column(sa.Text, nullable=False)

    document_type: sa.Mapped[DocumentType] = sa.mapped_column(
        sa.SAEnum(DocumentType, name="document_type", native_enum=False),
        nullable=False,
    )

    description: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    created_by: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        sa.Index("ix_document_org_id", "org_id"),
        sa.Index("ix_document_type", "document_type"),
        sa.Index("ix_document_created_by", "created_by"),
    )

    organization: sa.Mapped["Organization"] = sa.relationship("Organization", foreign_keys=[org_id])
    creator: sa.Mapped["User"] = sa.relationship("User", foreign_keys=[created_by])


class DocumentFile(UUIDPrimaryKeyMixin, TimestampsMixin, Base):
    __tablename__ = "document_file"

    document_id: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
    )

    org_id: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )

    storage_path: sa.Mapped[str] = sa.mapped_column(sa.Text, nullable=False)
    original_name: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)
    mime_type: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)
    file_size_bytes: sa.Mapped[int | None] = sa.mapped_column(sa.BigInteger, nullable=True)
    content_md5_b64: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    version_number: sa.Mapped[int] = sa.mapped_column(
        nullable=False,
        server_default=sa.text("1"),
    )
    is_latest: sa.Mapped[bool] = sa.mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )

    uploaded_by: sa.Mapped[str | None] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    uploaded_at: sa.Mapped[sa.DateTime] = sa.mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    parsing_status: sa.Mapped[ParsingStatus] = sa.mapped_column(
        sa.SAEnum(ParsingStatus, name="parsing_status", native_enum=False),
        nullable=False,
        server_default=sa.text(f"'{ParsingStatus.PENDING.value}'"),
    )

    parsed_at: sa.Mapped[sa.DateTime | None] = sa.mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )

    parsing_errors: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    parsed_suggestions: sa.Mapped[dict | None] = sa.mapped_column(sa.JSONB, nullable=True)

    __table_args__ = (
        sa.UniqueConstraint("document_id", "content_md5_b64", name="uq_document_file_doc_md5"),
        sa.Index("ix_document_file_document_id", "document_id"),
        sa.Index("ix_document_file_org_id", "org_id"),
        sa.Index("ix_document_file_parsing_status", "parsing_status"),
        sa.Index("ix_document_file_is_latest", "is_latest"),
        sa.Index("ix_document_file_parsed_suggestions", "parsed_suggestions"),
    )

    document: sa.Mapped["Document"] = sa.relationship("Document", foreign_keys=[document_id])
    uploader: sa.Mapped["User"] = sa.relationship("User", foreign_keys=[uploaded_by])
    organization: sa.Mapped["Organization"] = sa.relationship("Organization", foreign_keys=[org_id])
