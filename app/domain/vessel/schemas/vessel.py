from __future__ import annotations

from app.domain._shared.types import DateTime
from typing import Any

from pydantic import Field, field_validator

from app.domain._shared import RequestSchema, ResponseSchema, strip_or_none, PaginationParams
from .identity import VesselIdentityCreate, VesselIdentityRead
from .dimensions import VesselDimensionsCreate, VesselDimensionsRead
from .certificate import VesselCertificateBase, VesselCertificateRead

class VesselCreate(RequestSchema):
    """Client payload for creating a vessel."""

    name: str = Field(default="Unnamed Vessel", min_length=1)

    identity: VesselIdentityCreate | None = None
    dimensions: VesselDimensionsCreate | None = None
    certificates: list[VesselCertificateBase] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, v: Any) -> str:
        v = strip_or_none(v)
        return v or "Unnamed Vessel"

class VesselUpdate(RequestSchema):
    """Partial update for vessel."""
    name: str | None = None

class VesselListParams(PaginationParams):
    """Query params for listing vessels."""
    name: str | None = None
    vessel_type: str | None = None
    flag_state: str | None = None

class VesselRead(ResponseSchema):
    id: str
    org_id: str
    created_by: str | None

    name: str

    created_at: DateTime
    updated_at: DateTime

    identity: VesselIdentityRead | None = None
    dimensions: VesselDimensionsRead | None = None