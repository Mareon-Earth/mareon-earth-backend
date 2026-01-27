from __future__ import annotations

from abc import abstractmethod

from app.domain._shared.repository import BaseRepository
from app.domain.users.models import User


class UserRepositoryProtocol(BaseRepository[User, str]):
    @abstractmethod
    async def get_by_clerk_id(self, clerk_user_id: str) -> User | None: ...
    @abstractmethod
    async def update(self, user: User) -> User  : ...