from __future__ import annotations

from datetime import datetime
from pydantic import Field

from app.domain._shared import RequestSchema, ResponseSchema

class VesselDimensionsBase(RequestSchema):
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

class VesselDimensionsCreate(VesselDimensionsBase):
    ...


class VesselDimensionsRead(ResponseSchema):
    vessel_id: str

    loa_m: float | None
    lbp_m: float | None
    breadth_moulded_m: float | None
    depth_moulded_m: float | None

    created_at: datetime
    updated_at: datetime