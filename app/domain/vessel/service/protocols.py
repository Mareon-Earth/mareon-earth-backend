from __future__ import annotations

from typing import Protocol

from app.domain._shared.types import VesselId
from app.domain.vessel.schemas import VesselCreate, VesselRead


class VesselServiceProtocol(Protocol):
    async def create_vessel(self, payload: VesselCreate) -> VesselRead: ...

    async def get_vessel(self, vessel_id: VesselId) -> VesselRead: ...
