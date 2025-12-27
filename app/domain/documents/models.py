from __future__ import annotations

from app.infrastructure.db import Base
from app.infrastructure.db.sa import (
    String, Boolean, Integer,
    BigInteger, TIMESTAMP, ForeignKey,
    PrimaryKeyConstraint, Index, text,
    SAEnum, Mapped, mapped_column,
    relationship,
)

from app.infrastructure.db.mixins import (
    UUIDPrimaryKeyMixin, TimestampsMixin, CreatedAtMixin,
    OrgScopedMixin, CreatedByUserMixin,
)

from app.domain.documents.enums import DocumentType, DocumentProcessingStatus


class Document(UUIDPrimaryKeyMixin, OrgScopedMixin, CreatedByUserMixin, TimestampsMixin, Base):
    __tablename__ = "document"

    title: Mapped[str] = mapped_column(String, nullable=False)

    document_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type", native_enum=False),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(String, nullable=True)

    files: Mapped[list["DocumentFile"]] = relationship(
        "DocumentFile",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    vessel_links: Mapped[list["VesselDocument"]] = relationship(
        "VesselDocument",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    fleet_links: Mapped[list["FleetDocument"]] = relationship(
        "FleetDocument",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DocumentFile(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "document_file"

    document_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(String, nullable=False)

    original_name: Mapped[str | None] = mapped_column(String, nullable=True)
    file_extension: Mapped[str | None] = mapped_column(String, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True)

    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    hash_sha256: Mapped[str | None] = mapped_column(String, nullable=True)

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )

    is_latest: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    uploaded_by: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    uploaded_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Enforced by SQLAlchemy, stored as VARCHAR/TEXT (native_enum=False)
    processing_status: Mapped[DocumentProcessingStatus] = mapped_column(
        SAEnum(
            DocumentProcessingStatus,
            name="document_processing_status",
            native_enum=False,
        ),
        nullable=False,
        server_default=text(f"'{DocumentProcessingStatus.PENDING.value}'"),
    )

    processed_at: Mapped[str | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    processing_errors: Mapped[str | None] = mapped_column(String, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="files")

    __table_args__ = (
        # From dbdiagram: (document_id, hash_sha256) unique
        # Note: Postgres allows multiple NULLs in a unique index.
        Index(
            "ux_document_file_document_id_hash_sha256",
            "document_id",
            "hash_sha256",
            unique=True,
        ),
        Index("ix_document_file_document_id", "document_id"),
        Index("ix_document_file_processing_status", "processing_status"),
        Index("ix_document_file_is_latest", "is_latest"),
    )


class VesselDocument(CreatedAtMixin, Base):
    __tablename__ = "vessel_document"

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
    )

    document: Mapped["Document"] = relationship("Document", back_populates="vessel_links")

    __table_args__ = (
        PrimaryKeyConstraint("vessel_id", "document_id"),
        Index("ix_vessel_document_document_id", "document_id"),
    )


class FleetDocument(CreatedAtMixin, Base):
    __tablename__ = "fleet_document"

    fleet_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("fleet.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
    )

    document: Mapped["Document"] = relationship("Document", back_populates="fleet_links")

    __table_args__ = (
        PrimaryKeyConstraint("fleet_id", "document_id"),
        Index("ix_fleet_document_document_id", "document_id"),
    )
