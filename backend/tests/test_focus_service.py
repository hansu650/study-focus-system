from datetime import date, datetime, timedelta
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.base import Base
from app.db.models.focus import FocusSession
from app.db.models.points import PointLedger
from app.db.models.user import AppUser
from app.schemas.focus import FocusSessionCompleteRequest, FocusSessionStartRequest, FocusSessionStopRequest
from app.services.focus_service import FocusService


class FocusServiceLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            self.engine,
            tables=[AppUser.__table__, FocusSession.__table__, PointLedger.__table__],
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.db = self.SessionLocal()

        self.user = AppUser(
            user_id=1,
            username="demo_user",
            password_hash="x" * 60,
            nickname="Demo User",
            region_id=1,
            school_id=1,
            college_id=1,
            total_points=0,
            total_focus_minutes=0,
            status=1,
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def _create_running_session(self, started_minutes_ago: int, planned_minutes: int = 25, session_id: int = 1) -> FocusSession:
        session = FocusSession(
            session_id=session_id,
            user_id=self.user.user_id,
            focus_date=date.today(),
            planned_minutes=planned_minutes,
            actual_minutes=0,
            start_at=datetime.now() - timedelta(minutes=started_minutes_ago),
            end_at=None,
            status="RUNNING",
            lock_mode="APP_BLOCK",
            blocked_apps_json=None,
            blocked_sites_json=None,
            interrupt_count=0,
            awarded_points=0,
            settle_status=0,
            remark=None,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def test_complete_session_rejects_early_completion_even_if_client_sends_full_minutes(self) -> None:
        session = self._create_running_session(started_minutes_ago=1, planned_minutes=25)

        with self.assertRaises(ValueError) as ctx:
            FocusService.complete_session(
                self.db,
                self.user,
                session.session_id,
                FocusSessionCompleteRequest(actual_minutes=25),
            )

        self.assertIn("still running", str(ctx.exception))

        persisted_session = self.db.get(FocusSession, session.session_id)
        persisted_user = self.db.get(AppUser, self.user.user_id)
        self.assertEqual(persisted_session.status, "RUNNING")
        self.assertEqual(persisted_user.total_points, 0)
        self.assertEqual(persisted_user.total_focus_minutes, 0)

    def test_complete_session_awards_points_after_planned_duration(self) -> None:
        session = self._create_running_session(started_minutes_ago=26, planned_minutes=25)

        def fake_append_points_ledger(db, user, change_points, biz_type, biz_id, note):
            before = int(user.total_points)
            after = before + change_points
            ledger = PointLedger(
                txn_id=1,
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

        with patch.object(FocusService, "_append_points_ledger", side_effect=fake_append_points_ledger):
            result = FocusService.complete_session(
                self.db,
                self.user,
                session.session_id,
                FocusSessionCompleteRequest(actual_minutes=1),
            )

        persisted_user = self.db.get(AppUser, self.user.user_id)
        ledger = self.db.query(PointLedger).one()

        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(result.actual_minutes, 25)
        self.assertEqual(result.awarded_points, 25)
        self.assertEqual(persisted_user.total_points, 25)
        self.assertEqual(persisted_user.total_focus_minutes, 25)
        self.assertEqual(ledger.change_points, 25)
        self.assertEqual(ledger.biz_type, "FOCUS_REWARD")

    def test_interrupt_session_preserves_elapsed_minutes_for_resume(self) -> None:
        session = self._create_running_session(started_minutes_ago=10, planned_minutes=25)

        result = FocusService.interrupt_session(
            self.db,
            self.user,
            session.session_id,
            FocusSessionStopRequest(),
        )

        self.assertEqual(result.status, "INTERRUPTED")
        self.assertEqual(result.actual_minutes, 10)
        self.assertEqual(result.interrupt_count, 1)
        self.assertEqual(result.settle_status, 0)
        self.assertIsNotNone(result.end_at)

    def test_resume_session_restores_running_state_from_interrupted_session(self) -> None:
        session = self._create_running_session(started_minutes_ago=10, planned_minutes=25)
        FocusService.interrupt_session(self.db, self.user, session.session_id, FocusSessionStopRequest())

        result = FocusService.resume_session(self.db, self.user, session.session_id)
        estimated = FocusService._estimate_actual_minutes(result, datetime.now())

        self.assertEqual(result.status, "RUNNING")
        self.assertEqual(result.actual_minutes, 10)
        self.assertEqual(result.settle_status, 0)
        self.assertIsNone(result.end_at)
        self.assertEqual(estimated, 10)

    def test_resume_session_keeps_subminute_progress(self) -> None:
        session = FocusSession(
            session_id=9,
            user_id=self.user.user_id,
            focus_date=date.today(),
            planned_minutes=25,
            actual_minutes=0,
            start_at=datetime.now() - timedelta(seconds=45),
            end_at=None,
            status="RUNNING",
            lock_mode="APP_BLOCK",
            blocked_apps_json=None,
            blocked_sites_json=None,
            interrupt_count=0,
            awarded_points=0,
            settle_status=0,
            remark=None,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        paused = FocusService.interrupt_session(self.db, self.user, session.session_id, FocusSessionStopRequest())
        self.assertEqual(paused.actual_minutes, 0)
        saved_elapsed_seconds = (paused.end_at - paused.start_at).total_seconds()
        self.assertGreaterEqual(saved_elapsed_seconds, 40)

        resumed = FocusService.resume_session(self.db, self.user, session.session_id)
        resumed_elapsed_seconds = (datetime.now() - resumed.start_at).total_seconds()

        self.assertEqual(resumed.status, "RUNNING")
        self.assertGreaterEqual(resumed_elapsed_seconds, 40)
        self.assertLess(resumed_elapsed_seconds, 60)

    def test_start_session_rejects_new_session_when_interrupted_one_exists(self) -> None:
        session = self._create_running_session(started_minutes_ago=10, planned_minutes=25)
        FocusService.interrupt_session(self.db, self.user, session.session_id, FocusSessionStopRequest())

        with self.assertRaises(ValueError) as ctx:
            FocusService.start_session(
                self.db,
                self.user,
                FocusSessionStartRequest(planned_minutes=30),
            )

        self.assertIn("Resume or abandon", str(ctx.exception))

    def test_abandon_session_clears_elapsed_minutes(self) -> None:
        session = self._create_running_session(started_minutes_ago=8, planned_minutes=25)
        FocusService.interrupt_session(self.db, self.user, session.session_id, FocusSessionStopRequest())

        result = FocusService.abandon_session(
            self.db,
            self.user,
            session.session_id,
            FocusSessionStopRequest(),
        )

        self.assertEqual(result.status, "ABANDONED")
        self.assertEqual(result.actual_minutes, 0)
        self.assertEqual(result.awarded_points, 0)
        self.assertEqual(result.settle_status, 1)


if __name__ == "__main__":
    unittest.main()
