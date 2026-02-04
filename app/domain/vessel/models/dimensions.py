from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import TimestampsMixin

if TYPE_CHECKING:
    from .vessel import Vessel


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