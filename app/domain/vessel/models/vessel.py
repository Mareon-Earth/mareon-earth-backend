from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import (
    TimestampsMixin, UUIDPrimaryKeyMixin,
    OrgScopedMixin, CreatedByUserMixin,
)

if TYPE_CHECKING:
    from app.domain.organization.models import Organization
    from app.domain.users.models import User
    from .identity import VesselIdentity
    from .dimensions import VesselDimensions
    from .certificate import VesselCertificate


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
        lazy="selectin",
    )

    dimensions: sa.Mapped["VesselDimensions | None"] = sa.relationship(
        "VesselDimensions",
        back_populates="vessel",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    certificates: sa.Mapped[list["VesselCertificate"]] = sa.relationship(
        "VesselCertificate",
        back_populates="vessel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
