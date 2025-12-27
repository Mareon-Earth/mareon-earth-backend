from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_auth_context, AuthContext
from app.infrastructure.db import get_db_session
from app.services.organizations import OrganizationService
from app.domain.organization.schemas import OrganizationRead, OrgMemberRead

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/me", response_model=list[OrganizationRead])
async def list_my_organizations(
    ctx: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db_session),
):
    """
    List all organizations the current user belongs to.
    """
    # Get internal user ID from Clerk ID
    from app.services.users import UserService
    user = await UserService.get_user_by_clerk_id(db, ctx.user_id)
    
    orgs = await OrganizationService.list_user_organizations(db, user.id)
    return orgs


@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
):
    """
    Get organization details by ID.
    User must be a member of the organization (enforced by auth context).
    """
    org = await OrganizationService.get_organization(db, org_id)
    return org


@router.get("/{org_id}/members", response_model=list[OrgMemberRead])
async def list_organization_members(
    org_id: str,
    db: AsyncSession = Depends(get_db_session),
    ctx: AuthContext = Depends(get_auth_context),
):
    """
    List all members of an organization.
    User must be a member of the organization (enforced by auth context).
    """
    members = await OrganizationService.list_org_members(db, org_id)
    return members