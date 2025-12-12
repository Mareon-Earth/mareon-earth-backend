from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.models import User
from app.domain.users.schemas import UserCreate, UserUpdate


class UserRepository:
    """Database layer for the User domain."""

    @staticmethod
    async def get_by_clerk_id(db: AsyncSession, clerk_id: str) -> User | None:
        stmt = select(User).where(User.clerk_user_id == clerk_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: UserCreate) -> User:
        user = User(
            clerk_user_id=data.clerk_user_id,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            full_name=data.full_name,
            image_url=data.image_url,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update(db: AsyncSession, user: User, data: UserUpdate) -> User:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
