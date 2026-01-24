from typing import Optional
from pydantic import BaseModel, Field


class AuthContext(BaseModel):
    """
    Minimal auth context for a request.
    Assumption: every authenticated request is org-scoped.
    """

    user_id: str = Field(..., description="Clerk user id (sub)")
    organization_id: str = Field(..., description="Clerk organization id (org_id)")
    organization_role: Optional[str] = Field(
        None, description="Clerk org role (org_role)"
    )
    session_id: Optional[str] = Field(None, description="Clerk session id (sid)")
    internal_user_id: Optional[str] = Field(None, description="Internal user id")
    internal_org_id: Optional[str] = Field(None, description="Internal org id")

    class Config:
        frozen = True
