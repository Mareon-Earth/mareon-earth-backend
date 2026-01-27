from __future__ import annotations

from abc import abstractmethod

from app.domain._shared.repository import BaseRepository
from app.domain.organization.models import Organization, OrganizationMember


class OrganizationRepositoryProtocol(BaseRepository[Organization, str]):
    @abstractmethod
    async def get_by_clerk_id(self, clerk_org_id: str) -> Organization | None: ...
    @abstractmethod
    async def update(self, org: Organization) -> Organization  : ...

class OrganizationMemberRepositoryProtocol(BaseRepository[OrganizationMember, str]):
    @abstractmethod
    async def get_by_user_and_org(self, user_id: str, org_id: str) -> OrganizationMember | None: ...
    @abstractmethod
    async def update(self, member: OrganizationMember) -> OrganizationMember  : ...