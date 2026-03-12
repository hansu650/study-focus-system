import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.base import Base
from app.db.models.feedback import FeedbackMessage
from app.db.models.user import AppUser
from app.schemas.feedback import FeedbackCategory, FeedbackCreateRequest
from app.services.feedback_service import FeedbackService


class FeedbackServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            self.engine,
            tables=[AppUser.__table__, FeedbackMessage.__table__],
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.db = self.SessionLocal()

        self.user = AppUser(
            user_id=1,
            username="feedback-user",
            password_hash="x" * 60,
            nickname="Feedback User",
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

    def test_create_feedback_trims_and_persists_message(self) -> None:
        feedback = FeedbackService.create_feedback(
            self.db,
            self.user,
            FeedbackCreateRequest(
                category=FeedbackCategory.UI,
                title="  Add more calm colors  ",
                content="  The dashboard looks good, but the feedback card could feel softer.  ",
                contact_email="  demo@example.com  ",
            ),
        )

        self.assertEqual(feedback.user_id, self.user.user_id)
        self.assertEqual(feedback.category, "UI")
        self.assertEqual(feedback.title, "Add more calm colors")
        self.assertEqual(feedback.content, "The dashboard looks good, but the feedback card could feel softer.")
        self.assertEqual(feedback.contact_email, "demo@example.com")
        self.assertEqual(feedback.status, "NEW")

    def test_create_feedback_rejects_short_content_after_trim(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            FeedbackService.create_feedback(
                self.db,
                self.user,
                FeedbackCreateRequest(
                    category=FeedbackCategory.BUG,
                    title="Bug report",
                    content="      abc      ",
                ),
            )

        self.assertIn("at least 5 characters", str(ctx.exception))

    def test_list_my_feedback_returns_latest_first(self) -> None:
        FeedbackService.create_feedback(
            self.db,
            self.user,
            FeedbackCreateRequest(
                category=FeedbackCategory.GENERAL,
                title="First",
                content="First useful feedback message.",
            ),
        )
        FeedbackService.create_feedback(
            self.db,
            self.user,
            FeedbackCreateRequest(
                category=FeedbackCategory.IDEA,
                title="Second",
                content="Second useful feedback message.",
            ),
        )

        total, rows = FeedbackService.list_my_feedback(self.db, user_id=self.user.user_id, page=1, page_size=10)

        self.assertEqual(total, 2)
        self.assertEqual(rows[0].title, "Second")
        self.assertEqual(rows[1].title, "First")


if __name__ == "__main__":
    unittest.main()