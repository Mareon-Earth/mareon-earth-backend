from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import (
    TimestampsMixin, UUIDPrimaryKeyMixin,
    OrgScopedMixin, CreatedByUserMixin,
)

from .enums import VesselType

if TYPE_CHECKING:
    from app.domain.organization.models import Organization
    from app.domain.users.models import User


class Vessel(UUIDPrimaryKeyMixin, TimestampsMixin, CreatedByUserMixin, OrgScopedMixin, Base):
    __tablename__ = "vessel"

    name: sa.Mapped[str] = sa.mapped_column(
        sa.Text,
        nullable=False,
        default="Unnamed Vessel",
    )

    __table_args__ = (
        sa.Index("ix_vessel_org_id", "org_id"),
        sa.Index("ix_vessel_created_by", "created_by"),
        sa.Index("ix_vessel_name", "name"),
    )

    organization: sa.Mapped["Organization"] = sa.relationship(
        "Organization",
        foreign_keys="Vessel.org_id",
        lazy="selectin",
    )
    creator: sa.Mapped["User | None"] = sa.relationship(
        "User",
        foreign_keys="Vessel.created_by",
        lazy="selectin",
    )

    identity: sa.Mapped["VesselIdentity | None"] = sa.relationship(
        "VesselIdentity",
        back_populates="vessel",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    dimensions: sa.Mapped["VesselDimensions | None"] = sa.relationship(
        "VesselDimensions",
        back_populates="vessel",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class VesselIdentity(TimestampsMixin, Base):
    __tablename__ = "vessel_identity"

    vessel_id: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("vessel.id", ondelete="CASCADE"),
        primary_key=True,
    )

    imo_number: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)
    mmsi_number: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    call_sign: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)
    reported_name: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    vessel_type: sa.Mapped[VesselType] = sa.mapped_column(
        sa.SAEnum(VesselType, name="vessel_type", native_enum=False),
        nullable=False,
        server_default=sa.text(f"'{VesselType.OTHER.value}'"),
    )

    flag_state: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)
    port_of_registry: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    class_society: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)
    class_notation: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    __table_args__ = (
        sa.UniqueConstraint("imo_number", name="uq_vessel_identity_imo_number"),
        sa.UniqueConstraint("mmsi_number", name="uq_vessel_identity_mmsi_number"),
        sa.Index("ix_vessel_identity_vessel_id", "vessel_id"),
        sa.Index("ix_vessel_identity_imo_number", "imo_number"),
        sa.Index("ix_vessel_identity_mmsi_number", "mmsi_number"),
        sa.Index("ix_vessel_identity_port_of_registry", "port_of_registry"),
        sa.Index("ix_vessel_identity_vessel_type", "vessel_type"),
    )

    vessel: sa.Mapped["Vessel"] = sa.relationship(
        "Vessel",
        back_populates="identity",
        foreign_keys=[vessel_id],
    )


class VesselDimensions(TimestampsMixin, Base):
    __tablename__ = "vessel_dimensions"

    vessel_id: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("vessel.id", ondelete="CASCADE"),
        primary_key=True,
    )

    loa_m: sa.Mapped[float | None] = sa.mapped_column(sa.Float, nullable=True)
    lbp_m: sa.Mapped[float | None] = sa.mapped_column(sa.Float, nullable=True)
    breadth_moulded_m: sa.Mapped[float | None] = sa.mapped_column(sa.Float, nullable=True)
    depth_moulded_m: sa.Mapped[float | None] = sa.mapped_column(sa.Float, nullable=True)

    __table_args__ = (
        sa.Index("ix_vessel_dimensions_vessel_id", "vessel_id"),
    )

    vessel: sa.Mapped["Vessel"] = sa.relationship(
        "Vessel",
        back_populates="dimensions",
        foreign_keys=[vessel_id],
    )

class VesselCertificate(Base):
    """Vessel certificates."""
    
    __tablename__ = "vessel_certificate"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # 'class' | 'statutory'
    certificate_type_detail: Mapped[str | None] = mapped_column(String, nullable=True)

    issue_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    issue_location: Mapped[str | None] = mapped_column(String, nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="certificates")
    document: Mapped["Document"] = relationship()


class VesselSurvey(Base):
    """Vessel surveys."""
    
    __tablename__ = "vessel_survey"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # 'class' | 'statutory'
    survey_type: Mapped[str | None] = mapped_column(String, nullable=True)

    last_survey_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    last_survey_location: Mapped[str | None] = mapped_column(String, nullable=True)
    next_survey_from: Mapped[str | None] = mapped_column(Date, nullable=True)
    next_survey_due: Mapped[str | None] = mapped_column(Date, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)

    issuing_authority: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="surveys")
    document: Mapped["Document"] = relationship()


class VesselMemorandum(Base):
    """Vessel memoranda."""
    
    __tablename__ = "vessel_memorandum"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    vessel_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey("document.id", ondelete="SET NULL"),
        nullable=True,
    )

    memo_reference: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=False)

    issued_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    issued_location: Mapped[str | None] = mapped_column(String, nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    vessel: Mapped["Vessel"] = relationship(back_populates="memoranda")
    document: Mapped["Document"] = relationship()