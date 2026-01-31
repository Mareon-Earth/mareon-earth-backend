from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.domain._shared.types import OrganizationId, UserId, VesselId
from app.domain.organization.repository.protocols import OrganizationRepositoryProtocol
from app.domain.users.repository.protocols import UserRepositoryProtocol
from app.domain.vessel.exceptions import VesselAlreadyExistsError, VesselNotFoundError
from app.domain.vessel.models import Vessel, VesselIdentity
from app.domain.vessel.repository.protocols import (
    VesselIdentityRepositoryProtocol,
    VesselRepositoryProtocol,
)
from app.domain.vessel.schemas import VesselCreate, VesselIdentityRead, VesselRead
from app.domain.vessel.service.protocols import VesselServiceProtocol


class VesselService(VesselServiceProtocol):
    """
    Application service for vessel flows.

    Pattern matches DocumentService:
    - request-scoped
    - commits on success
    - rollbacks on any exception
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        vessels: VesselRepositoryProtocol,
        identities: VesselIdentityRepositoryProtocol,
        users: UserRepositoryProtocol,
        orgs: OrganizationRepositoryProtocol,
        ctx: AuthContext,
    ):
        self._db = db
        self._vessels = vessels
        self._identities = identities
        self._users = users
        self._orgs = orgs
        self._ctx = ctx

    async def create_vessel(self, payload: VesselCreate) -> VesselRead:
        try:
            org_id = await self._resolve_org_id()
            user_id = await self._resolve_user_id()

            # 1) Uniqueness checks (only if provided)
            if payload.identity:
                if payload.identity.imo_number:
                    existing = await self._identities.get_by_imo_number(payload.identity.imo_number)
                    if existing is not None:
                        raise VesselAlreadyExistsError(
                            metadata={"field": "imo_number", "value": payload.identity.imo_number}
                        )

                if payload.identity.mmsi_number:
                    existing = await self._identities.get_by_mmsi_number(payload.identity.mmsi_number)
                    if existing is not None:
                        raise VesselAlreadyExistsError(
                            metadata={"field": "mmsi_number", "value": payload.identity.mmsi_number}
                        )

            # 2) Build ORM objects
            vessel = Vessel(
                org_id=org_id,
                created_by=user_id,
                name=payload.name,
                vessel_type=payload.vessel_type,
            )

            if payload.identity is not None:
                ident = VesselIdentity(
                    imo_number=payload.identity.imo_number,
                    mmsi_number=payload.identity.mmsi_number,
                    call_sign=payload.identity.call_sign,
                    reported_name=payload.identity.reported_name,
                    reported_type=payload.identity.reported_type,
                    ais_ship_type=payload.identity.ais_ship_type,
                    flag_state=payload.identity.flag_state,
                    port_of_registry=payload.identity.port_of_registry,
                    class_society=payload.identity.class_society,
                    class_notation=payload.identity.class_notation,
                )
                vessel.identity = ident

            # 3) Persist
            await self._vessels.create(vessel)

            # 4) Commit
            await self._db.commit()

            # 5) Return read schema (from ORM)
            return self._to_vessel_read(vessel)

        except Exception:
            await self._db.rollback()
            raise

    async def get_vessel(self, vessel_id: VesselId) -> VesselRead:
        # (Optional) you may want org scoping here, but that depends on your auth model.
        vessel = await self._vessels.get_by_id(vessel_id)
        if vessel is None:
            raise VesselNotFoundError()

        return self._to_vessel_read(vessel)

    # -----------------------
    # helpers
    # -----------------------

    async def _resolve_org_id(self) -> OrganizationId:
        org_id = self._ctx.internal_org_id
        if org_id:
            return org_id

        org = await self._orgs.get_by_clerk_id(clerk_org_id=self._ctx.organization_id)
        if not org:
            # TODO: create OrganizationNotFoundError and use it here
            raise VesselNotFoundError(metadata={"reason": "org_not_found"})
        return org.id

    async def _resolve_user_id(self) -> UserId:
        user_id = self._ctx.internal_user_id
        if user_id:
            return user_id

        user = await self._users.get_by_clerk_id(clerk_user_id=self._ctx.user_id)
        if not user:
            # TODO: create UserNotFoundError and use it here
            raise VesselNotFoundError(metadata={"reason": "user_not_found"})
        return user.id

    def _to_vessel_read(self, vessel: Vessel) -> VesselRead:
        identity = None
        if vessel.identity is not None:
            identity = VesselIdentityRead(
                vessel_id=vessel.identity.vessel_id,
                imo_number=vessel.identity.imo_number,
                mmsi_number=vessel.identity.mmsi_number,
                call_sign=vessel.identity.call_sign,
                reported_name=vessel.identity.reported_name,
                reported_type=vessel.identity.reported_type,
                ais_ship_type=vessel.identity.ais_ship_type,
                flag_state=vessel.identity.flag_state,
                port_of_registry=vessel.identity.port_of_registry,
                class_society=vessel.identity.class_society,
                class_notation=vessel.identity.class_notation,
                created_at=vessel.identity.created_at,
                updated_at=vessel.identity.updated_at,
            )

        return VesselRead(
            id=vessel.id,
            org_id=vessel.org_id,
            created_by=vessel.created_by,
            name=vessel.name,
            vessel_type=vessel.vessel_type,
            created_at=vessel.created_at,
            updated_at=vessel.updated_at,
            identity=identity,
        )
