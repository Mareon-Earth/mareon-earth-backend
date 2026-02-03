from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from app.domain._shared import RequestSchema, ResponseSchema, strip_or_none
from .enums import VesselType


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
    dimensions: VesselDimensionsRead | None = None

class VesselDimensionsCreate(RequestSchema):
    """Vessel physical dimensions."""

    loa_m: float | None = Field(
        None,
        description="Length overall (LOA) in meters.",
    )
    lbp_m: float | None = Field(
        None,
        description="Length between perpendiculars (LBP) in meters.",
    )
    breadth_moulded_m: float | None = Field(
        None,
        description="Moulded breadth in meters.",
    )
    depth_moulded_m: float | None = Field(
        None,
        description="Moulded depth in meters.",
    )

    
class VesselDimensionsRead(ResponseSchema):
    vessel_id: str

    loa_m: float | None
    lbp_m: float | None
    breadth_moulded_m: float | None
    depth_moulded_m: float | None

    created_at: datetime
    updated_at: datetime