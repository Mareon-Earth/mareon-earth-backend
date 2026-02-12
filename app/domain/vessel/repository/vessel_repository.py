from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain._shared.types import VesselId, OrganizationId
from app.domain.vessel.models import Vessel, VesselIdentity
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

    async def list_by_org(
        self,
        org_id: OrganizationId,
        offset: int = 0,
        limit: int = 20,
        *,
        name: str | None = None,
        vessel_type: str | None = None,
        flag_state: str | None = None,
    ) -> tuple[list[Vessel], int]:
        # Build shared filter conditions
        filters = [Vessel.org_id == org_id]
        needs_identity_join = vessel_type is not None or flag_state is not None

        if name is not None:
            filters.append(Vessel.name.ilike(f"%{name}%"))
        if vessel_type is not None:
            filters.append(VesselIdentity.vessel_type == vessel_type)
        if flag_state is not None:
            filters.append(VesselIdentity.flag_state.ilike(f"%{flag_state}%"))

        # Count query
        count_stmt = select(func.count()).select_from(Vessel).where(*filters)
        if needs_identity_join:
            count_stmt = (
                select(func.count())
                .select_from(Vessel)
                .outerjoin(VesselIdentity, VesselIdentity.vessel_id == Vessel.id)
                .where(*filters)
            )
        total = (await self._db.execute(count_stmt)).scalar() or 0

        # Data query
        stmt = select(Vessel).where(*filters).offset(offset).limit(limit).order_by(Vessel.created_at.desc())
        if needs_identity_join:
            stmt = (
                select(Vessel)
                .outerjoin(VesselIdentity, VesselIdentity.vessel_id == Vessel.id)
                .where(*filters)
                .offset(offset)
                .limit(limit)
                .order_by(Vessel.created_at.desc())
            )
        result = await self._db.execute(stmt)
        vessels = list(result.scalars().all())
        return vessels, total

    async def count_by_org(self, org_id: OrganizationId) -> int:
        stmt = select(func.count()).select_from(Vessel).where(Vessel.org_id == org_id)
        return (await self._db.execute(stmt)).scalar() or 0
