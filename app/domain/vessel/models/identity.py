from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import TimestampsMixin

from app.domain.vessel.enums import VesselType

if TYPE_CHECKING:
    from .vessel import Vessel


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