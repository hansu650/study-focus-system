"""API endpoint tests for the Study Focus backend.

This suite uses FastAPI's TestClient with an in-memory SQLite database.
It is designed to test HTTP behavior without requiring a running MySQL server.

Recommended location:
    backend/tests/test_api_workflow_unittest.py

Run with:
    python -m unittest test_api_workflow_unittest.py -v
"""

from __future__ import annotations

import os
import unittest
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Optional test environment values.
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "120")

from app.core.security import hash_password
from app.db.models.base import Base
from app.db.models.daily_question import DailyQuestionAttempt
from app.db.models.dicts import DictCollege, DictRegion, DictSchool
from app.db.models.feedback import FeedbackMessage
from app.db.models.focus import FocusSession
from app.db.models.points import PointLedger
from app.db.models.user import AppUser
from app.db.session import get_db
from app.main import app


class ApiWorkflowTests(unittest.TestCase):
    """HTTP-level regression tests for the core backend workflow."""

    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False)

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

        self._seed_database()

        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.token = self._login_and_get_token()
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.engine.dispose()

    def _seed_database(self) -> None:
        db = self.SessionLocal()
        try:
            region = DictRegion(
                region_id=1,
                region_code="R-001",
                region_name="Test Region",
                region_level=1,
                parent_region_id=None,
            )
            school = DictSchool(
                school_id=1,
                school_code="S-001",
                school_name="Test University",
                region_id=1,
            )
            college = DictCollege(
                college_id=1,
                school_id=1,
                college_code="C-001",
                college_name="School of Engineering",
            )

            user = AppUser(
                user_id=101,
                username="api_user",
                password_hash=hash_password("StrongPass123"),
                nickname="API Tester",
                email="api_user@example.com",
                phone="1234567890",
                student_no="STU001",
                grade_year=2024,
                major_name="Software Engineering",
                region_id=1,
                school_id=1,
                college_id=1,
                total_points=30,
                total_focus_minutes=25,
                status=1,
            )

            another_user = AppUser(
                user_id=102,
                username="rank_user",
                password_hash=hash_password("StrongPass456"),
                nickname="Ranking User",
                email="rank_user@example.com",
                phone="1234567891",
                student_no="STU002",
                grade_year=2024,
                major_name="Computer Science",
                region_id=1,
                school_id=1,
                college_id=1,
                total_points=20,
                total_focus_minutes=60,
                status=1,
            )

            now = datetime.now()

            completed_session = FocusSession(
                session_id=201,
                user_id=101,
                focus_date=date.today(),
                planned_minutes=25,
                actual_minutes=25,
                start_at=now - timedelta(minutes=35),
                end_at=now - timedelta(minutes=10),
                status="COMPLETED",
                lock_mode="APP_BLOCK",
                blocked_apps_json=["Discord", "Steam"],
                blocked_sites_json=["youtube.com"],
                interrupt_count=0,
                awarded_points=25,
                settle_status=1,
                remark="Completed before API tests.",
            )

            running_session = FocusSession(
                session_id=202,
                user_id=101,
                focus_date=date.today(),
                planned_minutes=25,
                actual_minutes=0,
                start_at=now - timedelta(minutes=5),
                end_at=None,
                status="RUNNING",
                lock_mode="APP_BLOCK",
                blocked_apps_json=["WeChat"],
                blocked_sites_json=None,
                interrupt_count=0,
                awarded_points=0,
                settle_status=0,
                remark="Current active session.",
            )

            other_completed_session = FocusSession(
                session_id=203,
                user_id=102,
                focus_date=date.today(),
                planned_minutes=60,
                actual_minutes=60,
                start_at=now - timedelta(minutes=120),
                end_at=now - timedelta(minutes=60),
                status="COMPLETED",
                lock_mode="APP_BLOCK",
                blocked_apps_json=None,
                blocked_sites_json=None,
                interrupt_count=0,
                awarded_points=20,
                settle_status=1,
                remark="Leaderboard seed session.",
            )

            ledger_a = PointLedger(
                user_id=101,
                change_points=25,
                balance_before=5,
                balance_after=30,
                biz_type="FOCUS_REWARD",
                biz_id=201,
                note="Seeded focus reward.",
            )
            ledger_b = PointLedger(
                user_id=102,
                change_points=20,
                balance_before=0,
                balance_after=20,
                biz_type="FOCUS_REWARD",
                biz_id=203,
                note="Seeded focus reward.",
            )

            db.add_all(
                [
                    region,
                    school,
                    college,
                    user,
                    another_user,
                    completed_session,
                    running_session,
                    other_completed_session,
                    ledger_a,
                    ledger_b,
                ]
            )
            db.commit()
        finally:
            db.close()

    def _login_and_get_token(self) -> str:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"username": "api_user", "password": "StrongPass123"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("access_token", payload)
        return payload["access_token"]

    def test_health_endpoint_returns_ok(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_dictionary_endpoints_return_seeded_values(self) -> None:
        regions = self.client.get("/api/v1/dicts/regions")
        schools = self.client.get("/api/v1/dicts/schools", params={"region_id": 1})
        colleges = self.client.get("/api/v1/dicts/colleges", params={"school_id": 1})

        self.assertEqual(regions.status_code, 200)
        self.assertEqual(schools.status_code, 200)
        self.assertEqual(colleges.status_code, 200)

        self.assertEqual(regions.json()[0]["region_name"], "Test Region")
        self.assertEqual(schools.json()[0]["school_name"], "Test University")
        self.assertEqual(colleges.json()[0]["college_name"], "School of Engineering")

    def test_login_and_get_current_profile(self) -> None:
        response = self.client.get("/api/v1/users/me", headers=self.auth_headers)
        self.assertEqual(response.status_code, 200, response.text)

        payload = response.json()
        self.assertEqual(payload["username"], "api_user")
        self.assertEqual(payload["nickname"], "API Tester")
        self.assertEqual(payload["total_points"], 30)
        self.assertEqual(payload["total_focus_minutes"], 25)

    def test_daily_question_answer_adds_points(self) -> None:
        question_response = self.client.get("/api/v1/learning/daily-question", headers=self.auth_headers)
        self.assertEqual(question_response.status_code, 200, question_response.text)

        question_payload = question_response.json()
        correct_option = None
        today = question_payload["question_date"]

        # Look up the correct answer using the hint-free deterministic response after submission.
        # The backend returns the correct option in the answer response, so the test tries all options safely.
        for option in question_payload["options"]:
            answer_response = self.client.post(
                "/api/v1/learning/daily-question/answer",
                headers=self.auth_headers,
                json={
                    "question_date": today,
                    "selected_option": option["option_id"],
                },
            )
            self.assertEqual(answer_response.status_code, 201, answer_response.text)
            answer_payload = answer_response.json()
            correct_option = answer_payload["correct_option"]
            break

        self.assertIsNotNone(correct_option)

        balance_response = self.client.get("/api/v1/points/balance", headers=self.auth_headers)
        self.assertEqual(balance_response.status_code, 200)
        balance_payload = balance_response.json()

        expected_points = 35 if answer_payload["is_correct"] == 1 else 30
        self.assertEqual(balance_payload["total_points"], expected_points)

        ledger_response = self.client.get("/api/v1/points/ledger", headers=self.auth_headers)
        self.assertEqual(ledger_response.status_code, 200)
        self.assertGreaterEqual(ledger_response.json()["total"], 1)

    def test_feedback_create_and_list(self) -> None:
        create_response = self.client.post(
            "/api/v1/feedback",
            headers=self.auth_headers,
            json={
                "category": "BUG",
                "title": "Timer button overlap",
                "content": "The stop button overlaps the countdown label on a small screen.",
                "contact_email": "tester@example.com",
            },
        )
        self.assertEqual(create_response.status_code, 201, create_response.text)
        created_payload = create_response.json()
        self.assertEqual(created_payload["category"], "BUG")
        self.assertEqual(created_payload["status"], "NEW")

        list_response = self.client.get("/api/v1/feedback/my", headers=self.auth_headers)
        self.assertEqual(list_response.status_code, 200, list_response.text)
        list_payload = list_response.json()

        self.assertEqual(list_payload["total"], 1)
        self.assertEqual(list_payload["items"][0]["title"], "Timer button overlap")

    def test_focus_interrupt_resume_and_list(self) -> None:
        interrupt_response = self.client.post(
            "/api/v1/focus-sessions/202/interrupt",
            headers=self.auth_headers,
            json={},
        )
        self.assertEqual(interrupt_response.status_code, 200, interrupt_response.text)
        interrupted_payload = interrupt_response.json()
        self.assertEqual(interrupted_payload["status"], "INTERRUPTED")
        self.assertGreaterEqual(interrupted_payload["actual_minutes"], 0)

        resume_response = self.client.post(
            "/api/v1/focus-sessions/202/resume",
            headers=self.auth_headers,
        )
        self.assertEqual(resume_response.status_code, 200, resume_response.text)
        resumed_payload = resume_response.json()
        self.assertEqual(resumed_payload["status"], "RUNNING")
        self.assertIsNone(resumed_payload["end_at"])

        list_response = self.client.get(
            "/api/v1/focus-sessions",
            headers=self.auth_headers,
            params={"page": 1, "page_size": 10},
        )
        self.assertEqual(list_response.status_code, 200, list_response.text)
        list_payload = list_response.json()
        self.assertGreaterEqual(list_payload["total"], 2)

    def test_focus_leaderboard_returns_ranked_rows(self) -> None:
        response = self.client.get(
            "/api/v1/leaderboards/focus",
            headers=self.auth_headers,
            params={"period": "day", "scope": "school", "limit": 10},
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()

        self.assertEqual(payload["scope"], "school")
        self.assertEqual(payload["selected_school_name"], "Test University")
        self.assertGreaterEqual(len(payload["items"]), 2)
        self.assertEqual(payload["items"][0]["rank"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
