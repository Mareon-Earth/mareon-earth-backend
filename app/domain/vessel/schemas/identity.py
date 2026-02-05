from __future__ import annotations

from datetime import datetime
from pydantic import Field

from app.domain._shared import RequestSchema, ResponseSchema
from app.domain.vessel.enums import VesselType


class VesselIdentityCreate(RequestSchema):
    """
    Vessel identification data extracted from maritime documents.
    All fields optional to support incremental enrichment.
    """

    imo_number: str | None = Field(
        None,
        description="IMO ship identification number. 7 digits, no prefix.",
    )
    mmsi_number: str | None = Field(
        None,
        description="Maritime Mobile Service Identity. 9 digits.",
    )
    call_sign: str | None = Field(
        None,
        description="Radio call sign. 4-7 alphanumeric characters.",
    )
    reported_name: str | None = Field(
        None,
        description="Vessel name as stated in the document.",
    )
    vessel_type: VesselType = Field(
        VesselType.OTHER,
        description="Vessel category. Infer from type field, class notation, or document context.",
    )
    flag_state: str | None = Field(
        None,
        description="Flag state or country of registration.",
    )
    port_of_registry: str | None = Field(
        None,
        description="Port where the vessel is registered.",
    )
    class_society: str | None = Field(
        None,
        description="Classification society name (e.g., DNV, Lloyd's Register). Infer from document source if not explicit.",
    )
    class_notation: str | None = Field(
        None,
        description="Class notation with all symbols preserved verbatim (e.g., ✠1A1 or ⊕100A1). Do not normalize unicode.",
    )


class VesselIdentityUpdate(RequestSchema):
    """Partial update for vessel identity."""
    imo_number: str | None = None
    mmsi_number: str | None = None
    call_sign: str | None = None
    reported_name: str | None = None
    vessel_type: VesselType | None = None
    flag_state: str | None = None
    port_of_registry: str | None = None
    class_society: str | None = None
    class_notation: str | None = None


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