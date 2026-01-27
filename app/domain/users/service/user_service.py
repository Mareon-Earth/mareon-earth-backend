from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.users.models import User
from app.domain.users.repository.protocols import UserRepositoryProtocol
from app.domain.users.schemas import UserCreate, UserUpdate
from app.domain.users.service.protocols import UserServiceProtocol


class UserService(UserServiceProtocol):
    """
    Request-scoped service (holds AsyncSession).
    Routers should be thin: `return await svc.method(payload)`
    """

    def __init__(
        self,
        *,
        db: AsyncSession,
        users: UserRepositoryProtocol,
        ctx: AuthContext | None = None,
    ):
        self._db = db
        self._users = users
        self._ctx = ctx

    async def create_user(self, payload: UserCreate) -> User:
        try:
            existing = await self._users.get_by_clerk_id(payload.clerk_user_id)
            if existing:
                raise UserAlreadyExistsError()

            user = User(
                clerk_user_id=payload.clerk_user_id,
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                full_name=payload.full_name,
                image_url=payload.image_url,
            )
            await self._users.create(user)
            await self._db.commit()
            return user
        except Exception:
            await self._db.rollback()
            raise

    async def get_user(self, user_id: str) -> User:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> User:
        user = await self._users.get_by_clerk_id(clerk_user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def update_user_by_clerk_id(self, clerk_user_id: str, payload: UserUpdate) -> User:
        try:
            user = await self._users.get_by_clerk_id(clerk_user_id)
            if not user:
                raise UserNotFoundError()

            for field, value in payload.model_dump(exclude_unset=True).items():
                setattr(user, field, value)

            await self._users.update(user)
            await self._db.commit()
            return user
        except Exception:
            await self._db.rollback()
            raise

    async def delete_user_by_clerk_id(self, clerk_user_id: str) -> None:
        try:
            user = await self._users.get_by_clerk_id(clerk_user_id)
            if not user:
                raise UserNotFoundError()

            await self._users.delete(user.id)
            await self._db.commit()
        except Exception:
            await self._db.rollback()
            raise
