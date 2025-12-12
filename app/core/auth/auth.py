from fastapi import Request, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional


class AuthContext(BaseModel):
    """
    Represents the authenticated user + context from Clerk.
    Extend this later with roles, permissions, etc.
    """
    user_id: str
    organization_id: Optional[str] = None
    role: Optional[str] = None


async def get_auth_context(request: Request) -> AuthContext:
    """
    Temporary implementation until we add full Clerk JWT verification.
    For now:
    - Extract Authorization header (Bearer token)
    - Decode unverified payload (we will replace this soon)
    - Build AuthContext
    """

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    token = auth_header.removeprefix("Bearer ").strip()

    # For now, we pretend the token *is* the user_id (for local dev/testing)
    # Later: replace with Clerk JWKS decoding.
    # This avoids blocking your development.
    user_id = token  # TEMPORARY

    return AuthContext(user_id=user_id)
