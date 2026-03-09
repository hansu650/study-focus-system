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


class LeaderboardItemOut(BaseModel):
    """Single ranking item."""

    rank: int
    user_id: int
    username: str
    nickname: str
    total_points: int
    total_focus_minutes: int


class FocusLeaderboardOut(BaseModel):
    """Focus leaderboard response."""

    period: LeaderboardPeriod
    scope: LeaderboardScope
    date_start: date
    date_end: date
    items: list[LeaderboardItemOut]
