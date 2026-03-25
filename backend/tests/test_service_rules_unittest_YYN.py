"""Service-layer tests for the Study Focus backend.

This suite targets business rules directly and avoids the HTTP layer.
It is useful when you want faster feedback on core logic.

Recommended location:
    backend/tests/test_service_rules_unittest.py

Run with:
    python -m unittest test_service_rules_unittest.py -v
"""

from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.base import Base
from app.db.models.daily_question import DailyQuestionAttempt
from app.db.models.dicts import DictCollege, DictRegion, DictSchool
from app.db.models.feedback import FeedbackMessage
from app.db.models.focus import FocusSession
from app.db.models.points import PointLedger
from app.db.models.user import AppUser
from app.schemas.auth import LoginRequest
from app.schemas.feedback import FeedbackCreateRequest
from app.schemas.leaderboard import LeaderboardPeriod, LeaderboardScope
from app.schemas.user import UserUpdateRequest
from app.services.auth_service import AuthService
from app.services.daily_question_service import DailyQuestionService
from app.services.feedback_service import FeedbackService
from app.services.focus_service import FocusService
from app.services.leaderboard_service import LeaderboardService
from app.services.user_service import UserService
from app.core.security import hash_password


class ServiceRuleTests(unittest.TestCase):
    """Business-rule tests that run without the web framework."""

    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(
            self.engine,
            tables=[
                DictRegion.__table__,
                DictSchool.__table__,
                DictCollege.__table__,
                AppUser.__table__,
                PointLedger.__table__,
                DailyQuestionAttempt.__table__,
                FeedbackMessage.__table__,
                FocusSession.__table__,
            ],
        )
        self.db = self.SessionLocal()
        self._seed_database()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def _seed_database(self) -> None:
        self.db.add_all(
            [
                DictRegion(
                    region_id=1,
                    region_code="R-001",
                    region_name="Test Region",
                    region_level=1,
                    parent_region_id=None,
                ),
                DictSchool(
                    school_id=1,
                    school_code="S-001",
                    school_name="Test University",
                    region_id=1,
                ),
                DictCollege(
                    college_id=1,
                    school_id=1,
                    college_code="C-001",
                    college_name="Engineering",
                ),
                AppUser(
                    user_id=1,
                    username="service_user",
                    password_hash=hash_password("StrongPass123"),
                    nickname="Service User",
                    email="service_user@example.com",
                    phone="1111111111",
                    student_no="S001",
                    grade_year=2024,
                    major_name="Software Engineering",
                    region_id=1,
                    school_id=1,
                    college_id=1,
                    total_points=0,
                    total_focus_minutes=0,
                    status=1,
                ),
                AppUser(
                    user_id=2,
                    username="other_user",
                    password_hash=hash_password("StrongPass456"),
                    nickname="Other User",
                    email="other_user@example.com",
                    phone="2222222222",
                    student_no="S002",
                    grade_year=2024,
                    major_name="Computer Science",
                    region_id=1,
                    school_id=1,
                    college_id=1,
                    total_points=0,
                    total_focus_minutes=0,
                    status=1,
                ),
            ]
        )
        self.db.commit()
        self.user = self.db.get(AppUser, 1)
        self.other_user = self.db.get(AppUser, 2)

    def test_login_updates_last_login_time(self) -> None:
        self.assertIsNone(self.user.last_login_at)

        result = AuthService.login(
            self.db,
            LoginRequest(username="service_user", password="StrongPass123"),
        )

        self.assertEqual(result.user_id, 1)
        self.assertIsNotNone(result.last_login_at)

    def test_update_profile_rejects_duplicate_email(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            UserService.update_me(
                self.db,
                self.user,
                UserUpdateRequest(email="other_user@example.com"),
            )

        self.assertIn("Email is already used", str(ctx.exception))

    def test_feedback_service_trims_input_and_persists_message(self) -> None:
        feedback = FeedbackService.create_feedback(
            self.db,
            self.user,
            FeedbackCreateRequest(
                category="IDEA",
                title="  Add a dark mode toggle  ",
                content="  A desktop dark mode would reduce eye strain during long study sessions.  ",
                contact_email="  service_user@example.com  ",
            ),
        )

        self.assertEqual(feedback.title, "Add a dark mode toggle")
        self.assertTrue(feedback.content.startswith("A desktop dark mode"))
        self.assertEqual(feedback.contact_email, "service_user@example.com")

    def test_daily_question_rejects_non_today_submission(self) -> None:
        yesterday = date.today() - timedelta(days=1)

        with self.assertRaises(ValueError) as ctx:
            DailyQuestionService.submit_answer(
                db=self.db,
                user=self.user,
                question_date=yesterday,
                selected_option="A",
            )

        self.assertIn("Only today's daily question can be answered", str(ctx.exception))

    def test_daily_question_correct_answer_adds_points(self) -> None:
        today, question = DailyQuestionService.get_daily_question(date.today())

        attempt = DailyQuestionService.submit_answer(
            db=self.db,
            user=self.user,
            question_date=today,
            selected_option=question.correct_option,
        )

        refreshed_user = self.db.get(AppUser, self.user.user_id)
        ledger = self.db.query(PointLedger).filter(PointLedger.user_id == self.user.user_id).one()

        self.assertEqual(attempt.is_correct, 1)
        self.assertEqual(attempt.awarded_points, 5)
        self.assertEqual(refreshed_user.total_points, 5)
        self.assertEqual(ledger.biz_type, "QUESTION_REWARD")

    def test_resume_restores_running_state_for_interrupted_session(self) -> None:
        session = FocusSession(
            session_id=10,
            user_id=self.user.user_id,
            focus_date=date.today(),
            planned_minutes=25,
            actual_minutes=7,
            start_at=datetime.now() - timedelta(minutes=7),
            end_at=datetime.now(),
            status="INTERRUPTED",
            lock_mode="APP_BLOCK",
            blocked_apps_json=["Discord"],
            blocked_sites_json=None,
            interrupt_count=1,
            awarded_points=0,
            settle_status=0,
            remark="Paused once.",
        )
        self.db.add(session)
        self.db.commit()

        resumed = FocusService.resume_session(self.db, self.user, 10)

        self.assertEqual(resumed.status, "RUNNING")
        self.assertEqual(resumed.actual_minutes, 7)
        self.assertIsNone(resumed.end_at)
        self.assertEqual(resumed.interrupt_count, 1)

    def test_leaderboard_orders_by_points_then_focus_minutes(self) -> None:
        now = datetime.now()
        self.db.add_all(
            [
                PointLedger(
                    user_id=1,
                    change_points=20,
                    balance_before=0,
                    balance_after=20,
                    biz_type="FOCUS_REWARD",
                    biz_id=101,
                    note="Seed data for user 1.",
                ),
                PointLedger(
                    user_id=2,
                    change_points=20,
                    balance_before=0,
                    balance_after=20,
                    biz_type="FOCUS_REWARD",
                    biz_id=102,
                    note="Seed data for user 2.",
                ),
                FocusSession(
                    session_id=101,
                    user_id=1,
                    focus_date=date.today(),
                    planned_minutes=30,
                    actual_minutes=30,
                    start_at=now - timedelta(minutes=40),
                    end_at=now - timedelta(minutes=10),
                    status="COMPLETED",
                    lock_mode="APP_BLOCK",
                    blocked_apps_json=None,
                    blocked_sites_json=None,
                    interrupt_count=0,
                    awarded_points=20,
                    settle_status=1,
                    remark="Seed leaderboard record for user 1.",
                ),
                FocusSession(
                    session_id=102,
                    user_id=2,
                    focus_date=date.today(),
                    planned_minutes=50,
                    actual_minutes=50,
                    start_at=now - timedelta(minutes=90),
                    end_at=now - timedelta(minutes=20),
                    status="COMPLETED",
                    lock_mode="APP_BLOCK",
                    blocked_apps_json=None,
                    blocked_sites_json=None,
                    interrupt_count=0,
                    awarded_points=20,
                    settle_status=1,
                    remark="Seed leaderboard record for user 2.",
                ),
            ]
        )
        self.db.commit()

        result = LeaderboardService.get_focus_leaderboard(
            db=self.db,
            current_user=self.user,
            period=LeaderboardPeriod.DAY,
            scope=LeaderboardScope.SCHOOL,
            target_date=date.today(),
            school_id=None,
            college_id=None,
            limit=10,
        )

        self.assertEqual(result.selected_school_name, "Test University")
        self.assertGreaterEqual(len(result.items), 2)
        self.assertEqual(result.items[0].user_id, 2)
        self.assertEqual(result.items[0].total_points, 20)
        self.assertEqual(result.items[0].total_focus_minutes, 50)


if __name__ == "__main__":
    unittest.main(verbosity=2)
