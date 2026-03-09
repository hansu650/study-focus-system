"""Security helpers.

Provides password hashing/verification and JWT creation/parsing.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw_password: str) -> str:
    """Hash a plaintext password."""

    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against hash."""

    return pwd_context.verify(raw_password, hashed_password)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Create JWT access token.

    - subject: usually user id as string.
    - expires_minutes: optional override for token lifetime.
    """

    expire_delta = timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    expire_at = datetime.now(timezone.utc) + expire_delta
    payload: dict[str, Any] = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT token."""

    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def extract_subject(token: str) -> str:
    """Extract `sub` value from JWT token."""

    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise JWTError("Invalid token") from exc

    subject = payload.get("sub")
    if not subject:
        raise JWTError("Token subject missing")
    return str(subject)
