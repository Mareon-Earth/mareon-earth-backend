from pydantic import BaseModel
from typing import Optional
from app.domain._shared.types import DateTime
from app.domain.organization.models import OrganizationRole


class OrganizationBase(BaseModel):
    clerk_id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationRead(OrganizationBase):
    id: str
    created_at: DateTime
    updated_at: DateTime

    class Config:
        from_attributes = True


class OrganizationMemberBase(BaseModel):
    user_id: str
    org_id: str
    role: OrganizationRole


class OrganizationMemberCreate(OrganizationMemberBase):
    pass


class OrganizationMemberUpdate(BaseModel):
    role: Optional[OrganizationRole] = None


class OrganizationMemberRead(OrganizationMemberBase):
    created_at: DateTime
    updated_at: DateTime

    class Config:
        from_attributes = True