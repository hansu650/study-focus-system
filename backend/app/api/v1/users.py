"""User endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.user import AppUser
from app.db.session import get_db
from app.schemas.user import UserProfileOut, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileOut)
def get_me(current_user: Annotated[AppUser, Depends(get_current_user)]) -> UserProfileOut:
    """Get current user profile."""

    user = UserService.get_me(current_user)
    return UserProfileOut.model_validate(user)


@router.put("/me", response_model=UserProfileOut)
def update_me(
    payload: UserUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> UserProfileOut:
    """Update current user profile."""

    try:
        user = UserService.update_me(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return UserProfileOut.model_validate(user)
