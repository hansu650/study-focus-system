from datetime import date
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.base import Base
from app.db.models.daily_question import DailyQuestionAttempt
from app.db.models.points import PointLedger
from app.db.models.user import AppUser
from app.services.daily_question_service import DailyQuestionService


class DailyQuestionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            self.engine,
            tables=[AppUser.__table__, PointLedger.__table__, DailyQuestionAttempt.__table__],
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.db = self.SessionLocal()

        self.user = AppUser(
            user_id=1,
            username="quiz_user",
            password_hash="x" * 60,
            nickname="Quiz User",
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

    def test_submit_answer_awards_points_for_correct_choice(self) -> None:
        today, question = DailyQuestionService.get_daily_question(date.today())

        attempt = DailyQuestionService.submit_answer(
            db=self.db,
            user=self.user,
            question_date=today,
            selected_option=question.correct_option,
        )

        persisted_user = self.db.get(AppUser, self.user.user_id)
        ledger = self.db.query(PointLedger).one()

        self.assertEqual(attempt.question_date, today)
        self.assertEqual(attempt.selected_option, question.correct_option)
        self.assertEqual(attempt.is_correct, 1)
        self.assertEqual(attempt.awarded_points, 5)
        self.assertEqual(persisted_user.total_points, 5)
        self.assertEqual(ledger.change_points, 5)
        self.assertEqual(ledger.biz_type, "QUESTION_REWARD")
        self.assertEqual(attempt.points_txn_id, ledger.txn_id)

    def test_submit_answer_records_wrong_choice_without_points(self) -> None:
        today, question = DailyQuestionService.get_daily_question(date.today())
        wrong_option = next(option.option_id for option in question.options if option.option_id != question.correct_option)

        attempt = DailyQuestionService.submit_answer(
            db=self.db,
            user=self.user,
            question_date=today,
            selected_option=wrong_option,
        )

        persisted_user = self.db.get(AppUser, self.user.user_id)

        self.assertEqual(attempt.selected_option, wrong_option)
        self.assertEqual(attempt.is_correct, 0)
        self.assertEqual(attempt.awarded_points, 0)
        self.assertEqual(attempt.points_txn_id, None)
        self.assertEqual(persisted_user.total_points, 0)
        self.assertEqual(self.db.query(PointLedger).count(), 0)

    def test_submit_answer_rejects_duplicate_same_day_submission(self) -> None:
        today, question = DailyQuestionService.get_daily_question(date.today())

        DailyQuestionService.submit_answer(
            db=self.db,
            user=self.user,
            question_date=today,
            selected_option=question.correct_option,
        )

        with self.assertRaises(ValueError) as ctx:
            DailyQuestionService.submit_answer(
                db=self.db,
                user=self.user,
                question_date=today,
                selected_option=question.correct_option,
            )

        self.assertIn("already been answered", str(ctx.exception))
        self.assertEqual(self.db.query(DailyQuestionAttempt).count(), 1)


if __name__ == "__main__":
    unittest.main()
