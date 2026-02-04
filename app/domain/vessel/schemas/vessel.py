from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from app.domain._shared import RequestSchema, ResponseSchema, strip_or_none
from .identity import VesselIdentityCreate, VesselIdentityRead
from .dimensions import VesselDimensionsCreate, VesselDimensionsRead


class VesselCreate(RequestSchema):
    """
    Client payload for creating a vessel.
    org_id + created_by should come from auth/context, not from the client.
    """

    name: str = Field(default="Unnamed Vessel", min_length=1)

    identity: VesselIdentityCreate | None = None
    dimensions: VesselDimensionsCreate | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, v: Any) -> str:
        v = strip_or_none(v)
        return v or "Unnamed Vessel"


class VesselRead(ResponseSchema):
    id: str
    org_id: str
    created_by: str | None

    name: str

    created_at: datetime
    updated_at: datetime

    identity: VesselIdentityRead | None = None
    dimensions: VesselDimensionsRead | None = None