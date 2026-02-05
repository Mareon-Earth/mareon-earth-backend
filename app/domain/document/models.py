from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain._shared.types import DateTime
from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import UUIDPrimaryKeyMixin, TimestampsMixin

from .enums import DocumentType

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
        server_default=sa.text(f"'{DocumentType.OTHER.value}'"),
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
    files: sa.Mapped[list["DocumentFile"]] = sa.relationship(
        "DocumentFile",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


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

    # Full GCS URI (gs://bucket/path). NULL until upload is confirmed via Pub/Sub.
    source_uri: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

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

    requires_parsing: sa.Mapped[bool] = sa.mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.text("true"),
    )

    uploaded_by: sa.Mapped[str | None] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    uploaded_at: sa.Mapped[DateTime] = sa.mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    __table_args__ = (
        sa.UniqueConstraint("document_id", "content_md5_b64", name="uq_document_file_doc_md5"),
        sa.Index("ix_document_file_document_id", "document_id"),
        sa.Index("ix_document_file_org_id", "org_id"),
        sa.Index("ix_document_file_is_latest", "is_latest"),
        sa.Index(
            "ix_document_file_uploaded",
            "document_id",
            postgresql_where=sa.text("source_uri IS NOT NULL"),
        ),
    )

    document: sa.Mapped["Document"] = sa.relationship(
        "Document",
        foreign_keys=[document_id],
        back_populates="files",
    )
    uploader: sa.Mapped["User"] = sa.relationship("User", foreign_keys=[uploaded_by])
    organization: sa.Mapped["Organization"] = sa.relationship("Organization", foreign_keys=[org_id])

    @property
    def is_uploaded(self) -> bool:
        """True if the file has been successfully uploaded to GCS."""
        return self.source_uri is not None
