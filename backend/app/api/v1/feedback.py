"""Feedback endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.user import AppUser
from app.db.session import get_db
from app.schemas.feedback import FeedbackCreateRequest, FeedbackListOut, FeedbackOut
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> FeedbackOut:
    """Create one feedback message from the current user."""

    try:
        feedback = FeedbackService.create_feedback(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return FeedbackOut.model_validate(feedback)


@router.get("/my", response_model=FeedbackListOut)
def list_my_feedback(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> FeedbackListOut:
    """List the current user's recent feedback messages."""

    total, rows = FeedbackService.list_my_feedback(
        db=db,
        user_id=current_user.user_id,
        page=page,
        page_size=page_size,
    )

    return FeedbackListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=[FeedbackOut.model_validate(item) for item in rows],
    )