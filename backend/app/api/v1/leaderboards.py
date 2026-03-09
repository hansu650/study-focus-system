"""Leaderboard endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.user import AppUser
from app.db.session import get_db
from app.schemas.leaderboard import FocusLeaderboardOut, LeaderboardPeriod, LeaderboardScope
from app.services.leaderboard_service import LeaderboardService

router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])


@router.get("/focus", response_model=FocusLeaderboardOut)
def get_focus_leaderboard(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
    period: Annotated[LeaderboardPeriod, Query()] = LeaderboardPeriod.DAY,
    scope: Annotated[LeaderboardScope, Query()] = LeaderboardScope.SCHOOL,
    target_date: Annotated[date | None, Query(description="Reference date, default: today")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> FocusLeaderboardOut:
    """Get focus leaderboard for school or college scope."""

    return LeaderboardService.get_focus_leaderboard(
        db=db,
        current_user=current_user,
        period=period,
        scope=scope,
        target_date=target_date,
        limit=limit,
    )
