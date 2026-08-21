"""Clerk JWT verification for customer-facing authentication."""

import jwt
import httpx
import logging
from functools import lru_cache
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

_jwks_cache: dict = {}


def _get_jwks() -> dict:
    """Fetch and cache Clerk's JWKS public keys."""
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    try:
        response = httpx.get(settings.CLERK_JWKS_URL, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache
    except Exception as e:
        logger.error(f"Failed to fetch Clerk JWKS: {e}")
        raise HTTPException(status_code=503, detail="Auth service unavailable")


def _decode_clerk_token(token: str) -> dict:
    """Decode and verify a Clerk JWT token."""
    try:
        jwks = _get_jwks()
        # Get the signing key from JWKS
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        rsa_key = None
        for key in jwks.get("keys", []):
            if key["kid"] == kid:
                rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Invalid token signing key")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


class ClerkUser:
    """Represents an authenticated Clerk user."""

    def __init__(self, user_id: str, email: Optional[str] = None, name: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        self.name = name


async def get_clerk_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> ClerkUser:
    """FastAPI dependency: require a valid Clerk session token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    # In dev mode with placeholder key, accept any bearer token and return a mock user
    if settings.CLERK_SECRET_KEY == "sk_test_placeholder":
        return ClerkUser(user_id="dev_user_001", email="dev@example.com", name="Dev User")

    payload = _decode_clerk_token(credentials.credentials)
    return ClerkUser(
        user_id=payload.get("sub", ""),
        email=payload.get("email"),
        name=payload.get("name"),
    )


async def get_optional_clerk_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[ClerkUser]:
    """FastAPI dependency: optionally authenticate (returns None if no token)."""
    if not credentials:
        return None
    try:
        return await get_clerk_user(credentials)
    except HTTPException:
        return None
