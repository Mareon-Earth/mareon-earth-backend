from __future__ import annotations

from abc import abstractmethod

from app.domain._shared.repository import BaseRepository
from app.domain._shared.types import VesselId
from app.domain.vessel.models import Vessel, VesselIdentity


class VesselRepositoryProtocol(BaseRepository[Vessel, VesselId]):
    @abstractmethod
    async def update(self, vessel: Vessel) -> Vessel: ...


class VesselIdentityRepositoryProtocol(BaseRepository[VesselIdentity, VesselId]):
    @abstractmethod
    async def update(self, identity: VesselIdentity) -> VesselIdentity: ...

    @abstractmethod
    async def get_by_imo_number(self, imo_number: str) -> VesselIdentity | None: ...

    @abstractmethod
    async def get_by_mmsi_number(self, mmsi_number: str) -> VesselIdentity | None: ...
