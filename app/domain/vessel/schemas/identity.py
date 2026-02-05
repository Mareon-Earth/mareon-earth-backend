from __future__ import annotations

from app.domain._shared.types import DateTime
from pydantic import Field

from app.domain._shared import RequestSchema, ResponseSchema
from app.domain.vessel.enums import VesselType


class VesselIdentityCreate(RequestSchema):
    """Vessel identification data extracted from maritime documents."""

    imo_number: str | None = Field(None, description="IMO ship identification number (7 digits).")
    mmsi_number: str | None = Field(None, description="Maritime Mobile Service Identity (9 digits).")
    call_sign: str | None = Field(None, description="Radio call sign.")
    reported_name: str | None = Field(None, description="Vessel name as stated in the document.")
    vessel_type: VesselType = Field(VesselType.OTHER, description="Vessel category.")
    flag_state: str | None = Field(None, description="Flag state or country of registration.")
    port_of_registry: str | None = Field(None, description="Port where the vessel is registered.")
    class_society: str | None = Field(None, description="Classification society name (e.g., DNV).")
    class_notation: str | None = Field(None, description="Class notation, preserved verbatim.")


class VesselIdentityUpdate(RequestSchema):
    """Partial update for vessel identity."""
    call_sign: str | None
    reported_name: str | None
    vessel_type: VesselType | None

    flag_state: str | None
    port_of_registry: str | None

    class_society: str | None
    class_notation: str | None

    created_at: DateTime
    updated_at: DateTime


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

    created_at: DateTime
    updated_at: DateTime