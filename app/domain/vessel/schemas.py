from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from app.domain._shared import RequestSchema, ResponseSchema, strip_or_none
from .enums import VesselType


class VesselIdentityCreate(RequestSchema):
    """
    Optional nested identity payload for create-vessel.
    Keep all fields optional so you can create a vessel first and enrich later.
    """

    imo_number: str | None = None
    mmsi_number: str | None = None
    call_sign: str | None = None

    reported_name: str | None = None

    vessel_type: VesselType | None = None

    flag_state: str | None = None
    port_of_registry: str | None = None

    class_society: str | None = None
    class_notation: str | None = None

    _normalize = field_validator(
        "imo_number",
        "mmsi_number",
        "call_sign",
        "reported_name",
        "vessel_type",
        "flag_state",
        "port_of_registry",
        "class_society",
        "class_notation",
        mode="before",
    )(strip_or_none)

    @field_validator("imo_number")
    @classmethod
    def validate_imo(cls, v: str | None) -> str | None:
        if v is None:
            return None
        # IMO = 7 digits
        if not (len(v) == 7 and v.isdigit()):
            raise ValueError("imo_number must be 7 digits")
        return v

    @field_validator("mmsi_number")
    @classmethod
    def validate_mmsi(cls, v: str | None) -> str | None:
        if v is None:
            return None
        # MMSI = 9 digits
        if not (len(v) == 9 and v.isdigit()):
            raise ValueError("mmsi_number must be 9 digits")
        return v


class VesselCreate(RequestSchema):
    """
    Client payload for creating a vessel.
    org_id + created_by should come from auth/context, not from the client.
    """

    name: str = Field(default="Unnamed Vessel", min_length=1)

    identity: VesselIdentityCreate | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, v: Any) -> str:
        v = strip_or_none(v)
        return v or "Unnamed Vessel"


# Optional read schemas (useful for FastAPI response_model)
class VesselIdentityRead(ResponseSchema):
    vessel_id: str

    imo_number: str | None
    mmsi_number: str | None
    call_sign: str | None

    reported_name: str | None
    vessel_type: VesselType | None

    flag_state: str | None
    port_of_registry: str | None

    class_society: str | None
    class_notation: str | None

    created_at: datetime
    updated_at: datetime


class VesselRead(ResponseSchema):
    id: str
    org_id: str
    created_by: str | None

    name: str

    created_at: datetime
    updated_at: datetime

    identity: VesselIdentityRead | None = None
