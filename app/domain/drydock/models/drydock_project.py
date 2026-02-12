from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from app.domain._shared import Date
from app.domain.drydock.enums import DrydockProjectStatus
from app.infrastructure.db import Base
import app.infrastructure.db.sa as sa
from app.infrastructure.db.mixins import (
    TimestampsMixin,
    UUIDPrimaryKeyMixin,
    OrgScopedMixin,
    CreatedByUserMixin,
)

if TYPE_CHECKING:
    from app.domain.organization.models import Organization
    from app.domain.users.models import User
    from app.domain.vessel.models.vessel import Vessel


class DrydockProject(
    UUIDPrimaryKeyMixin,
    TimestampsMixin,
    CreatedByUserMixin,
    OrgScopedMixin,
    Base,
):
    __tablename__ = "drydock_project"

    vessel_id: sa.Mapped[UUID] = sa.mapped_column(
        sa.ForeignKey("vessel.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Optional human reference (e.g. "MOR/2024/DD01" from uploaded docs)
    reference: sa.Mapped[str | None] = sa.mapped_column(
        sa.Text,
        nullable=True,
    )

    title: sa.Mapped[str | None] = sa.mapped_column(
        sa.Text,
        nullable=True,
    )

    status: sa.Mapped[DrydockProjectStatus] = sa.mapped_column(
        sa.SAEnum(DrydockProjectStatus, name="drydock_project_status"),
        nullable=False,
        default=DrydockProjectStatus.PLANNING,
    )

    planned_start_date: sa.Mapped[Date | None] = sa.mapped_column(sa.Date, nullable=True)
    planned_end_date: sa.Mapped[Date | None] = sa.mapped_column(sa.Date, nullable=True)
    actual_start_date: sa.Mapped[Date | None] = sa.mapped_column(sa.Date, nullable=True)
    actual_end_date: sa.Mapped[Date | None] = sa.mapped_column(sa.Date, nullable=True)
