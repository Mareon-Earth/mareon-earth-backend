from __future__ import annotations

import asyncio
from fastapi import Request

from clerk_backend_api.security.types import AuthenticateRequestOptions

from app.core.auth.client import get_clerk
from app.core.auth.exceptions import MissingAuthTokenError, InvalidAuthTokenError


def extract_session_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.removeprefix("Bearer ").strip()

    cookie_token = request.cookies.get("__session")
    if cookie_token:
        return cookie_token

    raise MissingAuthTokenError()


async def verify_request_with_clerk(request: Request) -> dict:
    """
    Verifies the request with Clerk and returns the JWT payload dict.
    """
    # ensures clearer error if nothing was sent
    extract_session_token(request)

    clerk = get_clerk()

    # minimal options; Clerk will fetch JWKS if needed
    options = AuthenticateRequestOptions()

    state = await asyncio.to_thread(clerk.authenticate_request, request, options)

    if not getattr(state, "is_signed_in", False):
        reason = getattr(state, "reason", None)
        raise InvalidAuthTokenError(
            metadata={"reason": str(reason) if reason else None}
        )

    payload = getattr(state, "payload", None) or {}
    if not isinstance(payload, dict):
        raise InvalidAuthTokenError(metadata={"reason": "invalid_payload"})

    return payload
