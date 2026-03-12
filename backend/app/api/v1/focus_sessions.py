"""Focus session endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.user import AppUser
from app.db.session import get_db
from app.schemas.focus import (
    FocusSessionCompleteRequest,
    FocusSessionListOut,
    FocusSessionOut,
    FocusSessionStartRequest,
    FocusSessionStatus,
    FocusSessionStopRequest,
)
from app.services.focus_service import FocusService

router = APIRouter(prefix="/focus-sessions", tags=["Focus"])


@router.post("/start", response_model=FocusSessionOut, status_code=status.HTTP_201_CREATED)
def start_focus_session(
    payload: FocusSessionStartRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> FocusSessionOut:
    """Start one focus session for current user."""

    try:
        session = FocusService.start_session(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return FocusSessionOut.model_validate(session)


@router.post("/{session_id}/complete", response_model=FocusSessionOut)
def complete_focus_session(
    session_id: int,
    payload: FocusSessionCompleteRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> FocusSessionOut:
    """Complete a running focus session and settle points."""

    try:
        session = FocusService.complete_session(db, current_user, session_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return FocusSessionOut.model_validate(session)


@router.post("/{session_id}/interrupt", response_model=FocusSessionOut)
def interrupt_focus_session(
    session_id: int,
    payload: FocusSessionStopRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> FocusSessionOut:
    """Interrupt a running focus session."""

    try:
        session = FocusService.interrupt_session(db, current_user, session_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return FocusSessionOut.model_validate(session)


@router.post("/{session_id}/resume", response_model=FocusSessionOut)
def resume_focus_session(
    session_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> FocusSessionOut:
    """Resume an interrupted focus session."""

    try:
        session = FocusService.resume_session(db, current_user, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return FocusSessionOut.model_validate(session)


@router.post("/{session_id}/abandon", response_model=FocusSessionOut)
def abandon_focus_session(
    session_id: int,
    payload: FocusSessionStopRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> FocusSessionOut:
    """Abandon a running focus session."""

    try:
        session = FocusService.abandon_session(db, current_user, session_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return FocusSessionOut.model_validate(session)


@router.get("", response_model=FocusSessionListOut)
def list_my_focus_sessions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: Annotated[FocusSessionStatus | None, Query(alias="status")] = None,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> FocusSessionListOut:
    """List current user's focus sessions."""

    total, sessions = FocusService.list_sessions(
        db=db,
        user_id=current_user.user_id,
        page=page,
        page_size=page_size,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
    )

    return FocusSessionListOut(
        page=page,
        page_size=page_size,
        total=total,
        items=[FocusSessionOut.model_validate(item) for item in sessions],
    )
