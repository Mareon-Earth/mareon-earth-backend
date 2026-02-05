from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import VesselId
from app.domain.vessel.models import VesselDimensions
from app.domain.vessel.repository.protocols import VesselDimensionsRepositoryProtocol


class VesselDimensionsRepository(VesselDimensionsRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: VesselDimensions) -> VesselDimensions:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: VesselId) -> VesselDimensions | None:
        return await self._db.get(VesselDimensions, id)

    async def get_by_vessel_id(self, vessel_id: VesselId) -> VesselDimensions | None:
        stmt = select(VesselDimensions).where(VesselDimensions.vessel_id == vessel_id)
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none()

    async def delete(self, id: VesselId) -> None:
        dims = await self.get_by_id(id)
        if dims is not None:
            await self._db.delete(dims)
            await self._db.flush()

    async def update(self, dimensions: VesselDimensions) -> VesselDimensions:
        await self._db.flush()
        return dimensions