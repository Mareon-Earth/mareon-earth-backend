from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.models import User
from app.domain.users.schemas import UserCreate, UserUpdate

from app.domain.protocols.repositories import UserRepositoryProtocol
from typing import Optional

class UserRepository(UserRepositoryProtocol):
    """Repository layer for User model."""
    
    async def get_by_clerk_id(self, db: AsyncSession, clerk_user_id: str) -> Optional[User]:
        """Retrieve a user by their Clerk user ID."""
        stmt = select(User).where(User.clerk_user_id == clerk_user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_id(self, db: AsyncSession, user_id: str) -> User | None:
        """Retrieve a user by their ID."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, data: UserCreate) -> User:
        """Create a new user record."""
        user = User(
            clerk_user_id=data.clerk_user_id,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            full_name=data.full_name,
            image_url=data.image_url,
        )
        db.add(user)
        await db.flush()
        return user
    
    async def update(self, db: AsyncSession, user: User, data: UserUpdate) -> User:
        """Update an existing user record."""
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await db.flush()
        return user
    
    async def delete(self, db: AsyncSession, user: User) -> None:
        """Delete a user record."""
        await db.delete(user)
        await db.flush()
        