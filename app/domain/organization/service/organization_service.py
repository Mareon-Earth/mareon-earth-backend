from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.domain.organization.exceptions import (
    OrganizationAlreadyExistsError,
    OrganizationNotFoundError,
    OrganizationMemberNotFoundError,
    OrganizationMemberAlreadyExistsError,
)
from app.domain.organization.models import Organization, OrganizationMember
from app.domain.organization.repository.protocols import (
    OrganizationRepositoryProtocol,
    OrganizationMemberRepositoryProtocol,
)
from app.domain.organization.schemas import OrganizationCreate, OrganizationUpdate
from app.domain.organization.service.protocols import OrganizationServiceProtocol


class OrganizationService(OrganizationServiceProtocol):
    """
    Request-scoped service (holds AsyncSession).
    Routers should be thin: `return await svc.method(payload)`
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        organizations: OrganizationRepositoryProtocol,
        org_members: OrganizationMemberRepositoryProtocol,
        ctx: AuthContext | None = None,
    ):
        self._db = db
        self._organizations = organizations
        self._org_members = org_members
        self._ctx = ctx

    async def create_organization(self, payload: OrganizationCreate) -> Organization:
        try:
            existing = await self._organizations.get_by_clerk_id(payload.clerk_id)
            if existing:
                raise OrganizationAlreadyExistsError()

            org = Organization(
                clerk_id=payload.clerk_id,
                name=payload.name,
                logo_url=payload.logo_url,
            )
            await self._organizations.create(org)
            await self._db.commit()
            return org
        except Exception:
            await self._db.rollback()
            raise

    async def get_organization(self, organization_id: str) -> Organization:
        org = await self._organizations.get_by_id(organization_id)
        if not org:
            raise OrganizationNotFoundError()
        return org

    async def get_organization_by_clerk_id(self, clerk_org_id: str) -> Organization:
        org = await self._organizations.get_by_clerk_id(clerk_org_id)
        if not org:
            raise OrganizationNotFoundError()
        return org

    async def update_organization(
        self, organization_id: str, payload: OrganizationUpdate
    ) -> Organization:
        try:
            org = await self._organizations.get_by_id(organization_id)
            if not org:
                raise OrganizationNotFoundError()

            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(org, field, value)

            await self._organizations.update(org)
            await self._db.commit()
            return org
        except Exception:
            await self._db.rollback()
            raise

    async def delete_organization(self, organization_id: str) -> None:
        try:
            org = await self._organizations.get_by_id(organization_id)
            if not org:
                raise OrganizationNotFoundError()

            await self._organizations.delete(org.id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    async def add_member_to_organization(
        self, organization_id: str, user_id: str, role: str
    ) -> None:
        try:
            org = await self._organizations.get_by_id(organization_id)
            if not org:
                raise OrganizationNotFoundError()

            existing_member = await self._org_members.get_by_id((user_id, organization_id))
            if existing_member:
                raise OrganizationMemberAlreadyExistsError()

            member = OrganizationMember(
                org_id=organization_id,
                user_id=user_id,
                role=role,
            )
            await self._org_members.create(member)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise

    async def remove_member_from_organization(
        self, organization_id: str, user_id: str
    ) -> None:
        raise NotImplementedError()

    async def update_organization_member_role(
        self, organization_id: str, user_id: str, new_role: str
    ) -> None:
        raise NotImplementedError()