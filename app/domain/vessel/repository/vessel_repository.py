from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import VesselId
from app.domain.vessel.models import Vessel
from app.domain.vessel.repository.protocols import VesselRepositoryProtocol


class VesselRepository(VesselRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: Vessel) -> Vessel:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: VesselId) -> Vessel | None:
        return await self._db.get(Vessel, id)

    async def delete(self, id: VesselId) -> None:
        vessel = await self.get_by_id(id)
        if vessel is not None:
            await self._db.delete(vessel)
            await self._db.flush()

    async def update(self, vessel: Vessel) -> Vessel:
        # ORM tracks changes; flush pushes UPDATEs
        await self._db.flush()
        return vessel
