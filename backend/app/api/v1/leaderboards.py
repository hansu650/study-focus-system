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
    school_id: Annotated[int | None, Query(description="Optional school filter for school or college scope")] = None,
    college_id: Annotated[int | None, Query(description="Optional college filter for college scope")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> FocusLeaderboardOut:
    """Get focus leaderboard for college, school, or cross-school scope."""

    return LeaderboardService.get_focus_leaderboard(
        db=db,
        current_user=current_user,
        period=period,
        scope=scope,
        target_date=target_date,
        school_id=school_id,
        college_id=college_id,
        limit=limit,
    )