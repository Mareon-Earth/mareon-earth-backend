from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.domain._shared import PaginatedResponse
from app.domain._shared.types import OrganizationId, UserId, VesselId, CertificateId
from app.domain.organization.repository.protocols import OrganizationRepositoryProtocol
from app.domain.users.repository.protocols import UserRepositoryProtocol
from app.domain.vessel.exceptions import VesselAlreadyExistsError, VesselNotFoundError
from app.domain.vessel.models import Vessel, VesselIdentity, VesselDimensions, VesselCertificate
from app.domain.vessel.repository.protocols import (
    VesselIdentityRepositoryProtocol,
    VesselRepositoryProtocol,
    VesselDimensionsRepositoryProtocol,
    VesselCertificateRepositoryProtocol,
)
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
    VesselCertificateBase,
    VesselCertificateRead,
    VesselCertificateUpdate,
)
from app.domain.vessel.service.protocols import VesselServiceProtocol


class VesselService(VesselServiceProtocol):

    def __init__(
        self,
        *,
        db: AsyncSession,
        vessels: VesselRepositoryProtocol,
        identities: VesselIdentityRepositoryProtocol,
        dimensions: VesselDimensionsRepositoryProtocol,
        certificates: VesselCertificateRepositoryProtocol,
        users: UserRepositoryProtocol,
        orgs: OrganizationRepositoryProtocol,
        ctx: AuthContext,
    ):
        self._db = db
        self._vessels = vessels
        self._identities = identities
        self._dimensions = dimensions
        self._certificates = certificates
        self._users = users
        self._orgs = orgs
        self._ctx = ctx

    # ───────────────────────────────────────────────────────────────────
    # Core CRUD
    # ───────────────────────────────────────────────────────────────────

    async def create_vessel(self, payload: VesselCreate) -> VesselRead:
        try:
            org_id = await self._resolve_org_id()
            user_id = await self._resolve_user_id()

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

            vessel = Vessel(org_id=org_id, created_by=user_id, name=payload.name)

            if payload.identity is not None:
                vessel.identity = VesselIdentity(
                    imo_number=payload.identity.imo_number,
                    mmsi_number=payload.identity.mmsi_number,
                    call_sign=payload.identity.call_sign,
                    reported_name=payload.identity.reported_name,
                    vessel_type=payload.identity.vessel_type,
                    flag_state=payload.identity.flag_state,
                    port_of_registry=payload.identity.port_of_registry,
                    class_society=payload.identity.class_society,
                    class_notation=payload.identity.class_notation,
                )

            if payload.dimensions is not None:
                vessel.dimensions = VesselDimensions(
                    loa_m=payload.dimensions.loa_m,
                    lbp_m=payload.dimensions.lbp_m,
                    breadth_moulded_m=payload.dimensions.breadth_moulded_m,
                    depth_moulded_m=payload.dimensions.depth_moulded_m,
                )

            await self._vessels.create(vessel)
            await self._db.commit()
            return self._to_vessel_read(vessel)
        except Exception:
            await self._db.rollback()
            raise

    async def get_vessel(self, vessel_id: VesselId) -> VesselRead:
        vessel = await self._vessels.get_by_id(vessel_id)
        if vessel is None:
            raise VesselNotFoundError()
        return self._to_vessel_read(vessel)

    async def list_vessels(self, params: VesselListParams) -> PaginatedResponse[VesselRead]:
        try:
            org_id = await self._resolve_org_id()
            offset = (params.page - 1) * params.page_size
            vessels, total = await self._vessels.list_by_org(org_id, offset, params.page_size)
            return PaginatedResponse(
                items=[self._to_vessel_read(v) for v in vessels],
                total=total,
                page=params.page,
                page_size=params.page_size,
            )
        except Exception:
            await self._db.rollback()
            raise

    async def update_vessel(self, vessel_id: VesselId, payload: VesselUpdate) -> VesselRead:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()

            if payload.name is not None:
                vessel.name = payload.name

            await self._vessels.update(vessel)
            await self._db.commit()
            return self._to_vessel_read(vessel)
        except Exception:
            await self._db.rollback()
            raise

    async def delete_vessel(self, vessel_id: VesselId) -> None:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()
            await self._vessels.delete(vessel_id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    # ───────────────────────────────────────────────────────────────────
    # Identity management
    # ───────────────────────────────────────────────────────────────────

    async def upsert_identity(self, vessel_id: VesselId, payload: VesselIdentityCreate) -> VesselIdentityRead:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()

            if vessel.identity is None:
                vessel.identity = VesselIdentity(vessel_id=vessel_id)

            vessel.identity.imo_number = payload.imo_number
            vessel.identity.mmsi_number = payload.mmsi_number
            vessel.identity.call_sign = payload.call_sign
            vessel.identity.reported_name = payload.reported_name
            vessel.identity.vessel_type = payload.vessel_type
            vessel.identity.flag_state = payload.flag_state
            vessel.identity.port_of_registry = payload.port_of_registry
            vessel.identity.class_society = payload.class_society
            vessel.identity.class_notation = payload.class_notation

            await self._db.flush()
            await self._db.commit()
            return self._to_identity_read(vessel.identity)
        except Exception:
            await self._db.rollback()
            raise

    async def update_identity(self, vessel_id: VesselId, payload: VesselIdentityUpdate) -> VesselIdentityRead:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None or vessel.identity is None:
                raise VesselNotFoundError()

            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(vessel.identity, field, value)

            await self._identities.update(vessel.identity)
            await self._db.commit()
            return self._to_identity_read(vessel.identity)
        except Exception:
            await self._db.rollback()
            raise

    async def delete_identity(self, vessel_id: VesselId) -> None:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()
            if vessel.identity is not None:
                await self._identities.delete(vessel_id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    # ───────────────────────────────────────────────────────────────────
    # Dimensions management
    # ───────────────────────────────────────────────────────────────────

    async def upsert_dimensions(self, vessel_id: VesselId, payload: VesselDimensionsCreate) -> VesselDimensionsRead:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()

            if vessel.dimensions is None:
                vessel.dimensions = VesselDimensions(vessel_id=vessel_id)

            vessel.dimensions.loa_m = payload.loa_m
            vessel.dimensions.lbp_m = payload.lbp_m
            vessel.dimensions.breadth_moulded_m = payload.breadth_moulded_m
            vessel.dimensions.depth_moulded_m = payload.depth_moulded_m

            await self._db.flush()
            await self._db.commit()
            return self._to_dimensions_read(vessel.dimensions)
        except Exception:
            await self._db.rollback()
            raise

    async def update_dimensions(self, vessel_id: VesselId, payload: VesselDimensionsUpdate) -> VesselDimensionsRead:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None or vessel.dimensions is None:
                raise VesselNotFoundError()

            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(vessel.dimensions, field, value)

            await self._dimensions.update(vessel.dimensions)
            await self._db.commit()
            return self._to_dimensions_read(vessel.dimensions)
        except Exception:
            await self._db.rollback()
            raise

    async def delete_dimensions(self, vessel_id: VesselId) -> None:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()
            if vessel.dimensions is not None:
                await self._dimensions.delete(vessel_id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    # ───────────────────────────────────────────────────────────────────
    # Certificate management
    # ───────────────────────────────────────────────────────────────────

    async def list_certificates(
        self, vessel_id: VesselId, page: int, page_size: int
    ) -> PaginatedResponse[VesselCertificateRead]:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()

            offset = (page - 1) * page_size
            certs, total = await self._certificates.list_by_vessel(vessel_id, offset, page_size)
            return PaginatedResponse(
                items=[self._to_certificate_read(c) for c in certs],
                total=total,
                page=page,
                page_size=page_size,
            )
        except Exception:
            await self._db.rollback()
            raise

    async def create_certificate(
        self, vessel_id: VesselId, payload: VesselCertificateBase
    ) -> VesselCertificateRead:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()

            org_id = await self._resolve_org_id()
            user_id = await self._resolve_user_id()

            cert = VesselCertificate(
                vessel_id=vessel_id,
                org_id=org_id,
                created_by=user_id,
                domain=payload.domain,
                description=payload.description,
                identifier=payload.identifier,
                issuer=payload.issuer,
                issued_date=payload.issued_date,
                expiry_date=payload.expiry_date,
                status=payload.status,
            )
            await self._certificates.create(cert)
            await self._db.commit()
            return self._to_certificate_read(cert)
        except Exception:
            await self._db.rollback()
            raise

    async def get_certificate(
        self, vessel_id: VesselId, certificate_id: CertificateId
    ) -> VesselCertificateRead:
        vessel = await self._vessels.get_by_id(vessel_id)
        if vessel is None:
            raise VesselNotFoundError()

        cert = await self._certificates.get_by_id(certificate_id)
        if cert is None or cert.vessel_id != vessel_id:
            raise VesselNotFoundError(metadata={"reason": "certificate_not_found"})
        return self._to_certificate_read(cert)

    async def update_certificate(
        self, vessel_id: VesselId, certificate_id: CertificateId, payload: VesselCertificateUpdate
    ) -> VesselCertificateRead:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()

            cert = await self._certificates.get_by_id(certificate_id)
            if cert is None or cert.vessel_id != vessel_id:
                raise VesselNotFoundError(metadata={"reason": "certificate_not_found"})

            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(cert, field, value)

            await self._certificates.update(cert)
            await self._db.commit()
            return self._to_certificate_read(cert)
        except Exception:
            await self._db.rollback()
            raise

    async def delete_certificate(
        self, vessel_id: VesselId, certificate_id: CertificateId
    ) -> None:
        try:
            vessel = await self._vessels.get_by_id(vessel_id)
            if vessel is None:
                raise VesselNotFoundError()

            cert = await self._certificates.get_by_id(certificate_id)
            if cert is None or cert.vessel_id != vessel_id:
                raise VesselNotFoundError(metadata={"reason": "certificate_not_found"})

            await self._certificates.delete(certificate_id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    # ───────────────────────────────────────────────────────────────────
    # Helpers
    # ───────────────────────────────────────────────────────────────────

    async def _resolve_org_id(self) -> OrganizationId:
        org_id = self._ctx.internal_org_id
        if org_id:
            return org_id
        org = await self._orgs.get_by_clerk_id(clerk_org_id=self._ctx.organization_id)
        if not org:
            raise VesselNotFoundError(metadata={"reason": "org_not_found"})
        return org.id

    async def _resolve_user_id(self) -> UserId:
        user_id = self._ctx.internal_user_id
        if user_id:
            return user_id
        user = await self._users.get_by_clerk_id(clerk_user_id=self._ctx.user_id)
        if not user:
            raise VesselNotFoundError(metadata={"reason": "user_not_found"})
        return user.id

    def _to_vessel_read(self, vessel: Vessel) -> VesselRead:
        identity = self._to_identity_read(vessel.identity) if vessel.identity else None
        dimensions = self._to_dimensions_read(vessel.dimensions) if vessel.dimensions else None

        return VesselRead(
            id=vessel.id,
            org_id=vessel.org_id,
            created_by=vessel.created_by,
            name=vessel.name,
            created_at=vessel.created_at,
            updated_at=vessel.updated_at,
            identity=identity,
            dimensions=dimensions,
        )

    def _to_identity_read(self, identity: VesselIdentity) -> VesselIdentityRead:
        return VesselIdentityRead(
            vessel_id=identity.vessel_id,
            imo_number=identity.imo_number,
            mmsi_number=identity.mmsi_number,
            call_sign=identity.call_sign,
            reported_name=identity.reported_name,
            vessel_type=identity.vessel_type,
            flag_state=identity.flag_state,
            port_of_registry=identity.port_of_registry,
            class_society=identity.class_society,
            class_notation=identity.class_notation,
            created_at=identity.created_at,
            updated_at=identity.updated_at,
        )

    def _to_dimensions_read(self, dimensions: VesselDimensions) -> VesselDimensionsRead:
        return VesselDimensionsRead(
            vessel_id=dimensions.vessel_id,
            loa_m=dimensions.loa_m,
            lbp_m=dimensions.lbp_m,
            breadth_moulded_m=dimensions.breadth_moulded_m,
            depth_moulded_m=dimensions.depth_moulded_m,
            created_at=dimensions.created_at,
            updated_at=dimensions.updated_at,
        )

    def _to_certificate_read(self, cert: VesselCertificate) -> VesselCertificateRead:
        return VesselCertificateRead(
            id=cert.id,
            vessel_id=cert.vessel_id,
            domain=cert.domain,
            description=cert.description,
            identifier=cert.identifier,
            issuer=cert.issuer,
            issued_date=cert.issued_date,
            expiry_date=cert.expiry_date,
            status=cert.status,
            created_at=cert.created_at,
            updated_at=cert.updated_at,
        )
