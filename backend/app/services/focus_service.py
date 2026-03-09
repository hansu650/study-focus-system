"""Focus session service."""

from datetime import date, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db.models.focus import FocusSession
from app.db.models.points import PointLedger
from app.db.models.user import AppUser
from app.schemas.focus import (
    FocusSessionCompleteRequest,
    FocusSessionStartRequest,
    FocusSessionStatus,
    FocusSessionStopRequest,
)


class FocusService:
    """Business service for focus session lifecycle and settlement."""

    POINTS_PER_FOCUS_MINUTE = 1

    @staticmethod
    def start_session(db: Session, user: AppUser, payload: FocusSessionStartRequest) -> FocusSession:
        """Start a new focus session for the current user."""

        running = db.scalar(
            select(FocusSession).where(
                and_(
                    FocusSession.user_id == user.user_id,
                    FocusSession.status == FocusSessionStatus.RUNNING.value,
                )
            )
        )
        if running:
            raise ValueError("A running focus session already exists. Complete or stop it first.")

        now = datetime.now()
        session = FocusSession(
            user_id=user.user_id,
            focus_date=now.date(),
            planned_minutes=payload.planned_minutes,
            actual_minutes=0,
            start_at=now,
            end_at=None,
            status=FocusSessionStatus.RUNNING.value,
            lock_mode=payload.lock_mode.value,
            blocked_apps_json=payload.blocked_apps,
            blocked_sites_json=payload.blocked_sites,
            interrupt_count=0,
            awarded_points=0,
            settle_status=0,
            remark=payload.remark,
        )

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def complete_session(
        db: Session,
        user: AppUser,
        session_id: int,
        payload: FocusSessionCompleteRequest,
    ) -> FocusSession:
        """Complete a running focus session and settle points."""

        session = FocusService._get_owned_session(db, user.user_id, session_id, for_update=True)
        if session.status != FocusSessionStatus.RUNNING.value:
            raise ValueError("Only a running session can be completed.")

        now = datetime.now()
        actual_minutes = payload.actual_minutes if payload.actual_minutes is not None else session.planned_minutes
        actual_minutes = FocusService._normalize_actual_minutes(actual_minutes, session.planned_minutes, allow_zero=False)

        user_locked = db.scalar(
            select(AppUser).where(AppUser.user_id == user.user_id).with_for_update()
        )
        if not user_locked:
            raise ValueError("Current user does not exist.")

        awarded_points = actual_minutes * FocusService.POINTS_PER_FOCUS_MINUTE
        FocusService._append_points_ledger(
            db=db,
            user=user_locked,
            change_points=awarded_points,
            biz_type="FOCUS_REWARD",
            biz_id=session.session_id,
            note="Focus session completed.",
        )

        user_locked.total_focus_minutes = int(user_locked.total_focus_minutes) + actual_minutes

        session.actual_minutes = actual_minutes
        session.end_at = now
        session.status = FocusSessionStatus.COMPLETED.value
        session.awarded_points = awarded_points
        session.settle_status = 1
        if payload.remark is not None:
            session.remark = payload.remark

        db.add(user_locked)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def interrupt_session(
        db: Session,
        user: AppUser,
        session_id: int,
        payload: FocusSessionStopRequest,
    ) -> FocusSession:
        """Interrupt a running session without point reward."""

        session = FocusService._get_owned_session(db, user.user_id, session_id, for_update=True)
        if session.status != FocusSessionStatus.RUNNING.value:
            raise ValueError("Only a running session can be interrupted.")

        now = datetime.now()
        estimated = FocusService._estimate_actual_minutes(session, now)
        actual_minutes = payload.actual_minutes if payload.actual_minutes is not None else estimated
        actual_minutes = FocusService._normalize_actual_minutes(actual_minutes, session.planned_minutes, allow_zero=True)

        session.actual_minutes = actual_minutes
        session.end_at = now
        session.status = FocusSessionStatus.INTERRUPTED.value
        session.interrupt_count = int(session.interrupt_count) + 1
        session.awarded_points = 0
        session.settle_status = 1
        if payload.remark is not None:
            session.remark = payload.remark

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def abandon_session(
        db: Session,
        user: AppUser,
        session_id: int,
        payload: FocusSessionStopRequest,
    ) -> FocusSession:
        """Abandon a running session without point reward."""

        session = FocusService._get_owned_session(db, user.user_id, session_id, for_update=True)
        if session.status != FocusSessionStatus.RUNNING.value:
            raise ValueError("Only a running session can be abandoned.")

        now = datetime.now()
        estimated = FocusService._estimate_actual_minutes(session, now)
        actual_minutes = payload.actual_minutes if payload.actual_minutes is not None else estimated
        actual_minutes = FocusService._normalize_actual_minutes(actual_minutes, session.planned_minutes, allow_zero=True)

        session.actual_minutes = actual_minutes
        session.end_at = now
        session.status = FocusSessionStatus.ABANDONED.value
        session.awarded_points = 0
        session.settle_status = 1
        if payload.remark is not None:
            session.remark = payload.remark

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def list_sessions(
        db: Session,
        user_id: int,
        page: int,
        page_size: int,
        status: FocusSessionStatus | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[int, list[FocusSession]]:
        """List focus sessions for one user with pagination and filters."""

        query = select(FocusSession).where(FocusSession.user_id == user_id)

        if status is not None:
            query = query.where(FocusSession.status == status.value)
        if date_from is not None:
            query = query.where(FocusSession.focus_date >= date_from)
        if date_to is not None:
            query = query.where(FocusSession.focus_date <= date_to)

        total_query = select(func.count()).select_from(query.subquery())
        total = int(db.scalar(total_query) or 0)

        rows = list(
            db.scalars(
                query.order_by(FocusSession.start_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return total, rows

    @staticmethod
    def _get_owned_session(db: Session, user_id: int, session_id: int, for_update: bool = False) -> FocusSession:
        query = select(FocusSession).where(
            and_(
                FocusSession.session_id == session_id,
                FocusSession.user_id == user_id,
            )
        )
        if for_update:
            query = query.with_for_update()

        session = db.scalar(query)
        if not session:
            raise ValueError("Focus session not found.")
        return session

    @staticmethod
    def _estimate_actual_minutes(session: FocusSession, now: datetime) -> int:
        elapsed_minutes = int((now - session.start_at).total_seconds() // 60)
        elapsed_minutes = max(0, elapsed_minutes)
        return min(elapsed_minutes, int(session.planned_minutes))

    @staticmethod
    def _normalize_actual_minutes(actual_minutes: int, planned_minutes: int, allow_zero: bool) -> int:
        min_value = 0 if allow_zero else 1
        if actual_minutes < min_value:
            raise ValueError(f"actual_minutes must be >= {min_value}.")
        if actual_minutes > int(planned_minutes):
            raise ValueError("actual_minutes cannot exceed planned_minutes.")
        return actual_minutes

    @staticmethod
    def _append_points_ledger(
        db: Session,
        user: AppUser,
        change_points: int,
        biz_type: str,
        biz_id: int,
        note: str,
    ) -> PointLedger:
        before = int(user.total_points)
        after = before + change_points
        if after < 0:
            raise ValueError("Point balance cannot be negative.")

        ledger = PointLedger(
            user_id=user.user_id,
            change_points=change_points,
            balance_before=before,
            balance_after=after,
            biz_type=biz_type,
            biz_id=biz_id,
            note=note,
        )

        user.total_points = after
        db.add(ledger)
        return ledger
