"""Leaderboard query service."""

from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db.models.focus import FocusSession
from app.db.models.user import AppUser
from app.schemas.leaderboard import (
    FocusLeaderboardOut,
    LeaderboardItemOut,
    LeaderboardPeriod,
    LeaderboardScope,
)


class LeaderboardService:
    """Service for leaderboard ranking queries."""

    @staticmethod
    def get_focus_leaderboard(
        db: Session,
        current_user: AppUser,
        period: LeaderboardPeriod,
        scope: LeaderboardScope,
        target_date: date | None,
        limit: int,
    ) -> FocusLeaderboardOut:
        """Build focus leaderboard for selected period and scope."""

        date_start, date_end = LeaderboardService._resolve_date_range(period, target_date)
        dt_start = datetime.combine(date_start, time.min)
        dt_end_exclusive = datetime.combine(date_end + timedelta(days=1), time.min)

        points_sum = func.coalesce(func.sum(FocusSession.awarded_points), 0).label("total_points")
        minutes_sum = func.coalesce(func.sum(FocusSession.actual_minutes), 0).label("total_focus_minutes")

        stmt = (
            select(
                AppUser.user_id.label("user_id"),
                AppUser.username.label("username"),
                AppUser.nickname.label("nickname"),
                points_sum,
                minutes_sum,
            )
            .join(FocusSession, FocusSession.user_id == AppUser.user_id)
            .where(
                and_(
                    FocusSession.status == "COMPLETED",
                    FocusSession.settle_status == 1,
                    FocusSession.end_at >= dt_start,
                    FocusSession.end_at < dt_end_exclusive,
                )
            )
        )

        if scope == LeaderboardScope.SCHOOL:
            stmt = stmt.where(AppUser.school_id == current_user.school_id)
        else:
            stmt = stmt.where(AppUser.college_id == current_user.college_id)

        rows = db.execute(
            stmt.group_by(AppUser.user_id, AppUser.username, AppUser.nickname)
            .order_by(points_sum.desc(), minutes_sum.desc(), AppUser.user_id.asc())
            .limit(limit)
        ).all()

        items = [
            LeaderboardItemOut(
                rank=index,
                user_id=int(row.user_id),
                username=str(row.username),
                nickname=str(row.nickname),
                total_points=int(row.total_points),
                total_focus_minutes=int(row.total_focus_minutes),
            )
            for index, row in enumerate(rows, start=1)
        ]

        return FocusLeaderboardOut(
            period=period,
            scope=scope,
            date_start=date_start,
            date_end=date_end,
            items=items,
        )

    @staticmethod
    def _resolve_date_range(period: LeaderboardPeriod, target_date: date | None) -> tuple[date, date]:
        base_date = target_date or date.today()

        if period == LeaderboardPeriod.DAY:
            return base_date, base_date

        if period == LeaderboardPeriod.MONTH:
            start = date(base_date.year, base_date.month, 1)
            if base_date.month == 12:
                next_month = date(base_date.year + 1, 1, 1)
            else:
                next_month = date(base_date.year, base_date.month + 1, 1)
            end = next_month - timedelta(days=1)
            return start, end

        start = date(base_date.year, 1, 1)
        end = date(base_date.year, 12, 31)
        return start, end
