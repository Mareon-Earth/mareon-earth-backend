from __future__ import annotations

from typing import Protocol

from app.domain._shared import PaginatedResponse
from app.domain._shared.types import VesselId
from app.domain.vessel.schemas import (
    VesselCreate,
    VesselRead,
    VesselUpdate,
    VesselListParams,
    VesselIdentityCreate,
    VesselIdentityRead,
    VesselIdentityUpdate,
    VesselDimensionsCreate,
    VesselDimensionsRead,
    VesselDimensionsUpdate,
)


class VesselServiceProtocol(Protocol):
    # Core CRUD
    async def create_vessel(self, payload: VesselCreate) -> VesselRead: ...
    async def get_vessel(self, vessel_id: VesselId) -> VesselRead: ...
    async def list_vessels(self, params: VesselListParams) -> PaginatedResponse[VesselRead]: ...
    async def update_vessel(self, vessel_id: VesselId, payload: VesselUpdate) -> VesselRead: ...
    async def delete_vessel(self, vessel_id: VesselId) -> None: ...

    # Identity management
    async def upsert_identity(self, vessel_id: VesselId, payload: VesselIdentityCreate) -> VesselIdentityRead: ...
    async def update_identity(self, vessel_id: VesselId, payload: VesselIdentityUpdate) -> VesselIdentityRead: ...
    async def delete_identity(self, vessel_id: VesselId) -> None: ...

    # Dimensions management
    async def upsert_dimensions(self, vessel_id: VesselId, payload: VesselDimensionsCreate) -> VesselDimensionsRead: ...
    async def update_dimensions(self, vessel_id: VesselId, payload: VesselDimensionsUpdate) -> VesselDimensionsRead: ...
    async def delete_dimensions(self, vessel_id: VesselId) -> None: ...
