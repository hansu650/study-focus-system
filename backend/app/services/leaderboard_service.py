"""Leaderboard query service."""

from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db.models.dicts import DictCollege, DictSchool
from app.db.models.focus import FocusSession
from app.db.models.points import PointLedger
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
        school_id: int | None = None,
        college_id: int | None = None,
    ) -> FocusLeaderboardOut:
        """Build focus leaderboard for selected period and scope."""

        date_start, date_end = LeaderboardService._resolve_date_range(period, target_date)
        dt_start = datetime.combine(date_start, time.min)
        dt_end_exclusive = datetime.combine(date_end + timedelta(days=1), time.min)

        selected_school_id = school_id or current_user.school_id
        selected_college_id = college_id or current_user.college_id

        points_subquery = (
            select(
                PointLedger.user_id.label("user_id"),
                func.coalesce(func.sum(PointLedger.change_points), 0).label("earned_points"),
            )
            .where(
                and_(
                    PointLedger.biz_type.in_(("FOCUS_REWARD", "QUESTION_REWARD")),
                    PointLedger.occurred_at >= dt_start,
                    PointLedger.occurred_at < dt_end_exclusive,
                )
            )
            .group_by(PointLedger.user_id)
            .subquery()
        )

        minutes_subquery = (
            select(
                FocusSession.user_id.label("user_id"),
                func.coalesce(func.sum(FocusSession.actual_minutes), 0).label("focus_minutes"),
            )
            .where(
                and_(
                    FocusSession.status == "COMPLETED",
                    FocusSession.settle_status == 1,
                    FocusSession.end_at >= dt_start,
                    FocusSession.end_at < dt_end_exclusive,
                )
            )
            .group_by(FocusSession.user_id)
            .subquery()
        )

        points_sum = func.coalesce(points_subquery.c.earned_points, 0).label("total_points")
        minutes_sum = func.coalesce(minutes_subquery.c.focus_minutes, 0).label("total_focus_minutes")

        stmt = (
            select(
                AppUser.user_id.label("user_id"),
                AppUser.username.label("username"),
                AppUser.nickname.label("nickname"),
                AppUser.school_id.label("school_id"),
                DictSchool.school_name.label("school_name"),
                AppUser.college_id.label("college_id"),
                DictCollege.college_name.label("college_name"),
                points_sum,
                minutes_sum,
            )
            .join(DictSchool, DictSchool.school_id == AppUser.school_id)
            .join(DictCollege, DictCollege.college_id == AppUser.college_id)
            .outerjoin(points_subquery, points_subquery.c.user_id == AppUser.user_id)
            .outerjoin(minutes_subquery, minutes_subquery.c.user_id == AppUser.user_id)
            .where(or_(points_sum > 0, minutes_sum > 0))
        )

        selected_school_name = None
        selected_college_name = None

        if scope == LeaderboardScope.SCHOOL:
            stmt = stmt.where(AppUser.school_id == selected_school_id)
            selected_school_name = LeaderboardService._get_school_name(db, selected_school_id)
        elif scope == LeaderboardScope.COLLEGE:
            stmt = stmt.where(
                and_(
                    AppUser.school_id == selected_school_id,
                    AppUser.college_id == selected_college_id,
                )
            )
            selected_school_name = LeaderboardService._get_school_name(db, selected_school_id)
            selected_college_name = LeaderboardService._get_college_name(db, selected_college_id)
        else:
            selected_school_id = None
            selected_college_id = None

        rows = db.execute(
            stmt.order_by(points_sum.desc(), minutes_sum.desc(), AppUser.user_id.asc()).limit(limit)
        ).all()

        items = [
            LeaderboardItemOut(
                rank=index,
                user_id=int(row.user_id),
                username=str(row.username),
                nickname=str(row.nickname),
                total_points=int(row.total_points),
                total_focus_minutes=int(row.total_focus_minutes),
                school_id=int(row.school_id),
                school_name=str(row.school_name) if row.school_name is not None else None,
                college_id=int(row.college_id),
                college_name=str(row.college_name) if row.college_name is not None else None,
            )
            for index, row in enumerate(rows, start=1)
        ]

        return FocusLeaderboardOut(
            period=period,
            scope=scope,
            date_start=date_start,
            date_end=date_end,
            selected_school_id=selected_school_id,
            selected_school_name=selected_school_name,
            selected_college_id=selected_college_id if scope == LeaderboardScope.COLLEGE else None,
            selected_college_name=selected_college_name,
            items=items,
        )

    @staticmethod
    def _get_school_name(db: Session, school_id: int | None) -> str | None:
        if school_id is None:
            return None
        school = db.scalar(select(DictSchool).where(DictSchool.school_id == school_id))
        return school.school_name if school else None

    @staticmethod
    def _get_college_name(db: Session, college_id: int | None) -> str | None:
        if college_id is None:
            return None
        college = db.scalar(select(DictCollege).where(DictCollege.college_id == college_id))
        return college.college_name if college else None

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
