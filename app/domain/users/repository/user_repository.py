from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.models import User
from app.domain.users.repository.protocols import UserRepositoryProtocol


class UserRepository(UserRepositoryProtocol):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, entity: User) -> User:
        self._db.add(entity)
        await self._db.flush()
        return entity

    async def get_by_id(self, id: str) -> User | None:
        return await self._db.get(User, id)

    async def delete(self, id: str) -> None:
        user = await self.get_by_id(id)
        if user is not None:
            await self._db.delete(user)
            await self._db.flush()

    async def update(self, user: User) -> User:
        await self._db.flush()
        return user

    async def get_by_clerk_id(self, clerk_user_id: str) -> User | None:
        stmt = select(User).where(User.clerk_user_id == clerk_user_id)
        res = await self._db.execute(stmt)
        return res.scalar_one_or_none()
