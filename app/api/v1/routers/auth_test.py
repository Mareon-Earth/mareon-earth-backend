from fastapi import APIRouter, Depends
from app.core.auth import AuthContext, get_auth_context

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/whoami")
async def whoami(ctx: AuthContext = Depends(get_auth_context)):
    return {
        "user_id": ctx.user_id,
        "organization_id": ctx.organization_id,
        "organization_role": ctx.organization_role,
        "session_id": ctx.session_id,
    }
