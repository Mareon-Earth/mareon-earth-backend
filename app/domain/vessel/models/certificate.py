from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain._shared.types import Date
from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import (
    TimestampsMixin, UUIDPrimaryKeyMixin,
    OrgScopedMixin, CreatedByUserMixin,
)
from app.domain.vessel.enums import CertificateDomain, CertificateStatus

if TYPE_CHECKING:
    from .vessel import Vessel

class VesselCertificate(
    UUIDPrimaryKeyMixin,
    TimestampsMixin,
    OrgScopedMixin,
    CreatedByUserMixin,
    Base,
):
    __tablename__ = "vessel_certificate"

    vessel_id: sa.Mapped[str] = sa.mapped_column(
        sa.String,
        sa.ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    domain: sa.Mapped[CertificateDomain] = sa.mapped_column(
        sa.SAEnum(CertificateDomain, name="certificate_domain", native_enum=False),
        nullable=False,
        server_default=sa.text(f"'{CertificateDomain.OTHER.value}'"),
    )

    # Generic identifier: DNV "Code", ABS "Certificate Number", etc.
    identifier: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    # What you show in UI (certificate name/description)
    description: sa.Mapped[str] = sa.mapped_column(sa.Text, nullable=False)

    issuer: sa.Mapped[str | None] = sa.mapped_column(sa.Text, nullable=True)

    issued_date: sa.Mapped[Date | None] = sa.mapped_column(sa.Date, nullable=True)
    expiry_date: sa.Mapped[Date | None] = sa.mapped_column(sa.Date, nullable=True)

    status: sa.Mapped[CertificateStatus] = sa.mapped_column(
        sa.SAEnum(CertificateStatus, name="certificate_status", native_enum=False),
        nullable=False,
        server_default=sa.text(f"'{CertificateStatus.UNKNOWN.value}'"),
    )

    __table_args__ = (
        sa.Index("ix_vessel_certificate_org_id", "org_id"),
        sa.Index("ix_vessel_certificate_vessel_id", "vessel_id"),
        sa.Index("ix_vessel_certificate_domain", "domain"),
        sa.Index("ix_vessel_certificate_identifier", "identifier"),
        sa.Index("ix_vessel_certificate_expiry_date", "expiry_date"),
        sa.Index("ix_vessel_certificate_status", "status"),
    )

    vessel: sa.Mapped["Vessel"] = sa.relationship(
        "Vessel",
        back_populates="certificates",
        foreign_keys=[vessel_id],
        lazy="selectin",
    )