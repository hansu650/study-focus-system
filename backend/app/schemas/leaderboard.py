"""Leaderboard schemas."""

from datetime import date
from enum import Enum

from pydantic import BaseModel


class LeaderboardPeriod(str, Enum):
    """Supported ranking periods."""

    DAY = "day"
    MONTH = "month"
    YEAR = "year"


class LeaderboardScope(str, Enum):
    """Supported ranking scopes."""

    SCHOOL = "school"
    COLLEGE = "college"
    GLOBAL = "global"


class LeaderboardItemOut(BaseModel):
    """Single ranking item."""

    rank: int
    user_id: int
    username: str
    nickname: str
    total_points: int
    total_focus_minutes: int
    school_id: int
    school_name: str | None = None
    college_id: int
    college_name: str | None = None


class FocusLeaderboardOut(BaseModel):
    """Focus leaderboard response."""

    period: LeaderboardPeriod
    scope: LeaderboardScope
    date_start: date
    date_end: date
    selected_school_id: int | None = None
    selected_school_name: str | None = None
    selected_college_id: int | None = None
    selected_college_name: str | None = None
    items: list[LeaderboardItemOut]