from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.organization import (
    Organization,
    OrgMember,
    OrganizationRepository,
    OrgMemberRepository,
    OrganizationCreate,
    OrganizationUpdate,
    OrgMemberCreate,
    OrgMemberUpdate,
    OrganizationNotFoundError,
    OrgMemberNotFoundError,
    OrgRole,
)


class OrganizationService:
    """
    Service layer for organization operations.
    Organizations are managed by Clerk; this service handles local sync.
    """

    @staticmethod
    async def get_or_create_from_clerk(
        db: AsyncSession,
        payload: OrganizationCreate,
    ) -> Organization:
        """
        Used for Clerk webhook: ensure organization exists locally.
        """
        existing = await OrganizationRepository.get_by_clerk_id(db, payload.clerk_id)
        if existing:
            return existing

        return await OrganizationRepository.create(db, payload)

    @staticmethod
    async def update_organization(
        db: AsyncSession,
        clerk_org_id: str,
        payload: OrganizationUpdate,
    ) -> Organization:
        """
        Update organization from Clerk webhook.
        """
        org = await OrganizationRepository.get_by_clerk_id(db, clerk_org_id)
        if not org:
            raise OrganizationNotFoundError()

        return await OrganizationRepository.update(db, org, payload)

    @staticmethod
    async def delete_organization(
        db: AsyncSession,
        clerk_org_id: str,
    ) -> None:
        """
        Delete organization (triggered by Clerk webhook).
        Members are cascade-deleted via database constraints.
        """
        org = await OrganizationRepository.get_by_clerk_id(db, clerk_org_id)
        if not org:
            raise OrganizationNotFoundError()

        await OrganizationRepository.delete(db, org)

    @staticmethod
    async def get_organization(
        db: AsyncSession,
        org_id: str,
    ) -> Organization:
        """
        Get organization by internal ID.
        """
        org = await OrganizationRepository.get_by_id(db, org_id)
        if not org:
            raise OrganizationNotFoundError()
        return org

    @staticmethod
    async def get_organization_with_members(
        db: AsyncSession,
        org_id: str,
    ) -> Organization:
        """
        Get organization with members eagerly loaded.
        """
        org = await OrganizationRepository.get_by_id_with_members(db, org_id)
        if not org:
            raise OrganizationNotFoundError()
        return org

    @staticmethod
    async def list_user_organizations(
        db: AsyncSession,
        user_id: str,
    ) -> list[Organization]:
        """
        List all organizations a user belongs to.
        """
        return await OrganizationRepository.list_user_organizations(db, user_id)

    @staticmethod
    async def add_member(
        db: AsyncSession,
        user_id: str,
        org_id: str,
        role: OrgRole = OrgRole.MEMBER,
    ) -> OrgMember:
        """
        Add a member to an organization (triggered by Clerk webhook).
        """
        payload = OrgMemberCreate(user_id=user_id, org_id=org_id, role=role)
        return await OrgMemberRepository.create(db, payload)

    @staticmethod
    async def update_member_role(
        db: AsyncSession,
        user_id: str,
        org_id: str,
        role: OrgRole,
    ) -> OrgMember:
        """
        Update member role (triggered by Clerk webhook).
        """
        member = await OrgMemberRepository.get(db, user_id, org_id)
        if not member:
            raise OrgMemberNotFoundError()

        payload = OrgMemberUpdate(role=role)
        return await OrgMemberRepository.update(db, member, payload)

    @staticmethod
    async def remove_member(
        db: AsyncSession,
        user_id: str,
        org_id: str,
    ) -> None:
        """
        Remove member from organization (triggered by Clerk webhook).
        """
        member = await OrgMemberRepository.get(db, user_id, org_id)
        if not member:
            raise OrgMemberNotFoundError()

        await OrgMemberRepository.delete(db, member)

    @staticmethod
    async def list_org_members(
        db: AsyncSession,
        org_id: str,
    ) -> list[OrgMember]:
        """
        List all members of an organization.
        """
        return await OrgMemberRepository.list_org_members(db, org_id)