from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext
from app.domain.users.service.user_service import UserService
from app.domain.users.service.protocols import UserServiceProtocol
from app.domain.users.repository import UserRepository


def build_user_service(
    db: AsyncSession,
    ctx: AuthContext | None = None,
) -> UserServiceProtocol:
    user_repo = UserRepository(db)
    return UserService(db=db, users=user_repo, ctx=ctx)