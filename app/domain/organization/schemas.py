from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.domain.organization.models import OrgRole


# Organization Schemas
class OrganizationBase(BaseModel):
    clerk_id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating new organization entries (usually from Clerk webhook)."""
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationRead(OrganizationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# OrgMember Schemas
class OrgMemberBase(BaseModel):
    user_id: str
    org_id: str
    role: OrgRole = OrgRole.MEMBER


class OrgMemberCreate(OrgMemberBase):
    """Schema for adding a member to an organization."""
    pass


class OrgMemberUpdate(BaseModel):
    role: Optional[OrgRole] = None


class OrgMemberRead(OrgMemberBase):
    created_at: datetime

    class Config:
        from_attributes = True