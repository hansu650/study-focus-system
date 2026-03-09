"""API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import extract_subject
from app.db.models.user import AppUser
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> AppUser:
    """Resolve current authenticated user from JWT token."""

    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired login token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        subject = extract_subject(token)
        user_id = int(subject)
    except (JWTError, ValueError):
        raise credential_error

    user = db.scalar(
        select(AppUser).where(
            and_(
                AppUser.user_id == user_id,
                AppUser.status == 1,
                AppUser.deleted_at.is_(None),
            )
        )
    )
    if not user:
        raise credential_error

    return user
