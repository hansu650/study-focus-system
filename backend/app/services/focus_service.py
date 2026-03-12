"""Focus session service."""

from datetime import date, datetime, timedelta

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

        running = FocusService._get_running_session(db, user.user_id)
        if running:
            raise ValueError("A running focus session already exists. Complete or stop it first.")

        interrupted = FocusService._get_resumable_interrupted_session(db, user.user_id)
        if interrupted:
            raise ValueError("An interrupted focus session already exists. Resume or abandon it before starting a new one.")

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
        estimated = FocusService._estimate_actual_minutes(session, now)
        if estimated < int(session.planned_minutes):
            raise ValueError("Focus session is still running. Wait until the timer ends or interrupt it instead.")

        actual_minutes = int(session.planned_minutes)

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
        """Pause a running session and keep the elapsed time for resume."""

        session = FocusService._get_owned_session(db, user.user_id, session_id, for_update=True)
        if session.status != FocusSessionStatus.RUNNING.value:
            raise ValueError("Only a running session can be interrupted.")

        now = datetime.now()
        actual_minutes = FocusService._estimate_actual_minutes(session, now)

        session.actual_minutes = actual_minutes
        session.end_at = now
        session.status = FocusSessionStatus.INTERRUPTED.value
        session.interrupt_count = int(session.interrupt_count) + 1
        session.awarded_points = 0
        session.settle_status = 0
        if payload.remark is not None:
            session.remark = payload.remark

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def resume_session(
        db: Session,
        user: AppUser,
        session_id: int,
    ) -> FocusSession:
        """Resume an interrupted session without clearing its elapsed time."""

        session = FocusService._get_owned_session(db, user.user_id, session_id, for_update=True)
        if session.status != FocusSessionStatus.INTERRUPTED.value or int(session.settle_status) != 0:
            raise ValueError("Only an interrupted unfinished session can be resumed.")

        running = FocusService._get_running_session(db, user.user_id, for_update=True)
        if running and running.session_id != session.session_id:
            raise ValueError("Another running focus session already exists.")

        elapsed_delta = FocusService._resolve_saved_elapsed_delta(session)
        now = datetime.now()
        resumed_start = now - elapsed_delta

        session.start_at = resumed_start
        session.focus_date = resumed_start.date()
        session.end_at = None
        session.status = FocusSessionStatus.RUNNING.value
        session.awarded_points = 0
        session.settle_status = 0

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
        """Abandon a session and clear its elapsed time without point reward."""

        session = FocusService._get_owned_session(db, user.user_id, session_id, for_update=True)
        if session.status not in {FocusSessionStatus.RUNNING.value, FocusSessionStatus.INTERRUPTED.value}:
            raise ValueError("Only a running or interrupted session can be abandoned.")

        now = datetime.now()

        session.actual_minutes = 0
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
    def _get_running_session(db: Session, user_id: int, for_update: bool = False) -> FocusSession | None:
        query = select(FocusSession).where(
            and_(
                FocusSession.user_id == user_id,
                FocusSession.status == FocusSessionStatus.RUNNING.value,
            )
        )
        if for_update:
            query = query.with_for_update()
        return db.scalar(query)

    @staticmethod
    def _get_resumable_interrupted_session(db: Session, user_id: int) -> FocusSession | None:
        query = (
            select(FocusSession)
            .where(
                and_(
                    FocusSession.user_id == user_id,
                    FocusSession.status == FocusSessionStatus.INTERRUPTED.value,
                    FocusSession.settle_status == 0,
                )
            )
            .order_by(FocusSession.updated_at.desc(), FocusSession.session_id.desc())
        )
        return db.scalar(query)

    @staticmethod
    def _estimate_actual_minutes(session: FocusSession, now: datetime) -> int:
        elapsed_delta = FocusService._estimate_elapsed_delta(session, now)
        elapsed_minutes = int(elapsed_delta.total_seconds() // 60)
        return min(elapsed_minutes, int(session.planned_minutes))

    @staticmethod
    def _estimate_elapsed_delta(session: FocusSession, now: datetime) -> timedelta:
        elapsed_seconds = max(0.0, (now - session.start_at).total_seconds())
        planned_seconds = max(0, int(session.planned_minutes) * 60)
        return timedelta(seconds=min(elapsed_seconds, planned_seconds))

    @staticmethod
    def _resolve_saved_elapsed_delta(session: FocusSession) -> timedelta:
        planned_seconds = max(0, int(session.planned_minutes) * 60)

        if session.end_at is not None:
            elapsed_seconds = max(0.0, (session.end_at - session.start_at).total_seconds())
            return timedelta(seconds=min(elapsed_seconds, planned_seconds))

        fallback_minutes = FocusService._normalize_actual_minutes(
            int(session.actual_minutes or 0),
            int(session.planned_minutes),
            allow_zero=True,
        )
        return timedelta(minutes=fallback_minutes)

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
