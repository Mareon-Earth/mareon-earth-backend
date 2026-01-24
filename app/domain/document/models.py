from __future__ import annotations

import enum

from app.infrastructure.db import Base
from app.infrastructure.db.sa import (
    PrimaryKeyConstraint,
    String,
    Text,
    ForeignKey,
    Index,
    text,
    Mapped,
    mapped_column,
    relationship,
    SAEnum,
    BigInteger, # Added for DocumentFile
    Boolean,    # Added for DocumentFile
    DateTime,   # Added for DocumentFile
    UniqueConstraint, # Added for DocumentFile
)
from app.infrastructure.db.mixins import UUIDPrimaryKeyMixin, TimestampsMixin, CreatedAtMixin
from app.domain.organization.models import Organization
from app.domain.users import User

class DocumentContentType(str, enum.Enum):
    PDF = "PDF"
    IMAGE = "IMAGE"
    DOCX = "DOCX"
    XLSX = "XLSX"
    CSV = "CSV"
    PPTX = "PPTX"
    TXT = "TXT"
    OTHER = "OTHER"

class DocumentType(str, enum.Enum):
    CLASS_STATUS_REPORT = "CLASS_STATUS_REPORT"
    GA_PLAN = "GA_PLAN"
    MACHINERY_LIST = "MACHINERY_LIST"
    SURVEY_REPORT = "SURVEY_REPORT"
    CERTIFICATE = "CERTIFICATE"
    OTHER = "OTHER"


class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNSUPPORTED = "UNSUPPORTED"


class Document(UUIDPrimaryKeyMixin, TimestampsMixin, Base):
    __tablename__ = "document"

    org_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type", native_enum=False),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_document_org_id", "org_id"),
        Index("ix_document_type", "document_type"),
        Index("ix_document_created_by", "created_by"),
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        foreign_keys=[org_id],
    )
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )


class DocumentFile(UUIDPrimaryKeyMixin, TimestampsMixin, Base):
    __tablename__ = "document_file"

    document_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
    )

    # IMPORTANT: you need this if you want UNIQUE(org_id, md5)
    org_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    original_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Raw upload metadata (keep for debugging + edge cases)
    mime_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # GCS md5Hash (base64)
    content_md5_b64: Mapped[str | None] = mapped_column(Text, nullable=True)

    version_number: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    uploaded_by: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    uploaded_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SAEnum(ProcessingStatus, name="processing_status", native_enum=False),
        nullable=False,
        server_default=text(f"'{ProcessingStatus.PENDING.value}'"),
    )
    processed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_errors: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("org_id", "content_md5_b64", name="uq_document_file_org_md5"),
        Index("ix_document_file_document_id", "document_id"),
        Index("ix_document_file_org_id", "org_id"),
        Index("ix_document_file_processing_status", "processing_status"),
        Index("ix_document_file_is_latest", "is_latest"),
    )

    document: Mapped["Document"] = relationship("Document", foreign_keys=[document_id])
    uploader: Mapped["User"] = relationship("User", foreign_keys=[uploaded_by])
    organization: Mapped["Organization"] = relationship("Organization", foreign_keys=[org_id])

    
# class VesselDocument(CreatedAtMixin, Base):
#     __tablename__ = "vessel_document"

#     vessel_id: Mapped[str] = mapped_column(
#         String,
#         ForeignKey("vessel.id", ondelete="CASCADE"),
#         nullable=False,
#     )
#     document_id: Mapped[str] = mapped_column(
#         String,
#         ForeignKey("document.id", ondelete="CASCADE"),
#         nullable=False,
#     )

#     __table_args__ = (
#         PrimaryKeyConstraint("vessel_id", "document_id"),
#         Index("ix_vessel_document_document_id", "document_id"),
#     )

#     # Relationships will be added when vessel model is created
#     # vessel: Mapped["Vessel"] = relationship("Vessel", foreign_keys=[vessel_id])
#     document: Mapped["Document"] = relationship("Document", foreign_keys=[document_id])


# class FleetDocument(CreatedAtMixin, Base):
#     __tablename__ = "fleet_document"

#     fleet_id: Mapped[str] = mapped_column(
#         String,
#         ForeignKey("fleet.id", ondelete="CASCADE"),
#         nullable=False,
#     )
#     document_id: Mapped[str] = mapped_column(
#         String,
#         ForeignKey("document.id", ondelete="CASCADE"),
#         nullable=False,
#     )

#     __table_args__ = (
#         PrimaryKeyConstraint("fleet_id", "document_id"),
#         Index("ix_fleet_document_document_id", "document_id"),
#     )

#     # Relationships will be added when fleet model is created
#     # fleet: Mapped["Fleet"] = relationship("Fleet", foreign_keys=[fleet_id])
#     document: Mapped["Document"] = relationship("Document", foreign_keys=[document_id])

