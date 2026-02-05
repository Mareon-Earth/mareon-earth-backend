from __future__ import annotations

from abc import abstractmethod

from app.domain._shared.repository import BaseRepository
from app.domain._shared.types import VesselId, OrganizationId, CertificateId
from app.domain.vessel.models import Vessel, VesselIdentity, VesselDimensions, VesselCertificate


class VesselRepositoryProtocol(BaseRepository[Vessel, VesselId]):
    @abstractmethod
    async def update(self, vessel: Vessel) -> Vessel: ...

    @abstractmethod
    async def list_by_org(
        self, org_id: OrganizationId, offset: int = 0, limit: int = 20
    ) -> tuple[list[Vessel], int]: ...

    @abstractmethod
    async def count_by_org(self, org_id: OrganizationId) -> int: ...


class VesselIdentityRepositoryProtocol(BaseRepository[VesselIdentity, VesselId]):
    @abstractmethod
    async def update(self, identity: VesselIdentity) -> VesselIdentity: ...

    @abstractmethod
    async def get_by_imo_number(self, imo_number: str) -> VesselIdentity | None: ...

    @abstractmethod
    async def get_by_mmsi_number(self, mmsi_number: str) -> VesselIdentity | None: ...


class VesselDimensionsRepositoryProtocol(BaseRepository[VesselDimensions, VesselId]):
    @abstractmethod
    async def update(self, dimensions: VesselDimensions) -> VesselDimensions: ...

    @abstractmethod
    async def get_by_vessel_id(self, vessel_id: VesselId) -> VesselDimensions | None: ...


class VesselCertificateRepositoryProtocol(BaseRepository[VesselCertificate, CertificateId]):
    @abstractmethod
    async def update(self, certificate: VesselCertificate) -> VesselCertificate: ...

    @abstractmethod
    async def list_by_vessel(
        self, vessel_id: VesselId, offset: int = 0, limit: int = 20
    ) -> tuple[list[VesselCertificate], int]: ...
