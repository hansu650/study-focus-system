"""Daily question service."""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.daily_question import DailyQuestionAttempt
from app.db.models.points import PointLedger
from app.db.models.user import AppUser


@dataclass(frozen=True)
class DailyQuestionOption:
    """One selectable option in the daily quiz."""

    option_id: str
    content: str


@dataclass(frozen=True)
class DailyQuestion:
    """Question record for daily push."""

    subject: str
    difficulty: str
    title: str
    question: str
    answer_hint: str
    options: tuple[DailyQuestionOption, ...]
    correct_option: str


class DailyQuestionService:
    """Serve deterministic daily question from local question bank."""

    REWARD_POINTS = 5
    REWARD_BIZ_TYPE = "QUESTION_REWARD"

    QUESTION_BANK: tuple[DailyQuestion, ...] = (
        DailyQuestion(
            subject="Computer Science",
            difficulty="Easy",
            title="Time Complexity",
            question="What is the time complexity of binary search on a sorted array?",
            answer_hint="Think about halving the search interval after each comparison.",
            options=(
                DailyQuestionOption("A", "O(1) because the midpoint is computed once."),
                DailyQuestionOption("B", "O(log n) because each step halves the remaining search space."),
                DailyQuestionOption("C", "O(n) because items may still need to be checked one by one."),
                DailyQuestionOption("D", "O(n log n) because the array is sorted before each search."),
            ),
            correct_option="B",
        ),
        DailyQuestion(
            subject="Mathematics",
            difficulty="Medium",
            title="Derivative Basics",
            question="For f(x)=x^3-4x+2, what is f'(2)?",
            answer_hint="Differentiate first, then substitute x=2 into the derivative.",
            options=(
                DailyQuestionOption("A", "0"),
                DailyQuestionOption("B", "4"),
                DailyQuestionOption("C", "8"),
                DailyQuestionOption("D", "12"),
            ),
            correct_option="C",
        ),
        DailyQuestion(
            subject="Physics",
            difficulty="Medium",
            title="Kinematics",
            question="A body starts from rest and accelerates at 2 m/s^2 for 5 s. How far does it travel?",
            answer_hint="Use s = ut + 1/2*a*t^2 and remember u starts at zero.",
            options=(
                DailyQuestionOption("A", "10 m"),
                DailyQuestionOption("B", "20 m"),
                DailyQuestionOption("C", "25 m"),
                DailyQuestionOption("D", "50 m"),
            ),
            correct_option="C",
        ),
        DailyQuestion(
            subject="English",
            difficulty="Easy",
            title="Grammar",
            question="Which sentence correctly changes 'The team finished the project yesterday.' into the passive voice?",
            answer_hint="Move the object forward and use a past passive verb phrase.",
            options=(
                DailyQuestionOption("A", "The project was finished by the team yesterday."),
                DailyQuestionOption("B", "The project finished yesterday by the team."),
                DailyQuestionOption("C", "Yesterday the team has finished the project."),
                DailyQuestionOption("D", "The project is finished by the team yesterday."),
            ),
            correct_option="A",
        ),
        DailyQuestion(
            subject="Computer Science",
            difficulty="Hard",
            title="Database Index",
            question="When is an index most likely to hurt performance instead of help it?",
            answer_hint="Think about write-heavy tables and low-selectivity columns.",
            options=(
                DailyQuestionOption("A", "When the table is queried often by highly selective keys."),
                DailyQuestionOption("B", "When the workload is mostly inserts and updates on a low-selectivity column."),
                DailyQuestionOption("C", "When the indexed column is used in WHERE clauses."),
                DailyQuestionOption("D", "When the query planner can use covering indexes."),
            ),
            correct_option="B",
        ),
        DailyQuestion(
            subject="Chemistry",
            difficulty="Easy",
            title="Periodic Table",
            question="Which element has the chemical symbol Na?",
            answer_hint="It is a soft metal often found in table salt compounds.",
            options=(
                DailyQuestionOption("A", "Nitrogen"),
                DailyQuestionOption("B", "Neon"),
                DailyQuestionOption("C", "Sodium"),
                DailyQuestionOption("D", "Nickel"),
            ),
            correct_option="C",
        ),
        DailyQuestion(
            subject="History",
            difficulty="Easy",
            title="Ancient Civilization",
            question="Which river is most closely associated with ancient Egyptian civilization?",
            answer_hint="It flows from south to north through Egypt.",
            options=(
                DailyQuestionOption("A", "Yangtze"),
                DailyQuestionOption("B", "Amazon"),
                DailyQuestionOption("C", "Danube"),
                DailyQuestionOption("D", "Nile"),
            ),
            correct_option="D",
        ),
    )

    @staticmethod
    def ensure_attempt_storage(db: Session) -> None:
        """Create the attempt table on demand for local/dev databases."""

        DailyQuestionAttempt.__table__.create(bind=db.get_bind(), checkfirst=True)

    @staticmethod
    def get_daily_question(target_date: date | None = None, subject: str | None = None) -> tuple[date, DailyQuestion]:
        """Return one deterministic daily question by date and optional subject."""

        day = target_date or date.today()
        pool = DailyQuestionService.QUESTION_BANK

        if subject:
            subject_key = subject.strip().lower()
            filtered = tuple(item for item in pool if item.subject.lower() == subject_key)
            if not filtered:
                raise ValueError("No daily question available for the requested subject.")
            pool = filtered

        index = day.toordinal() % len(pool)
        return day, pool[index]

    @staticmethod
    def get_attempt(db: Session, user_id: int, question_date: date) -> DailyQuestionAttempt | None:
        """Return today's stored answer, if any."""

        DailyQuestionService.ensure_attempt_storage(db)

        return db.scalar(
            select(DailyQuestionAttempt).where(
                DailyQuestionAttempt.user_id == user_id,
                DailyQuestionAttempt.question_date == question_date,
            )
        )

    @staticmethod
    def submit_answer(
        db: Session,
        user: AppUser,
        question_date: date,
        selected_option: str,
    ) -> DailyQuestionAttempt:
        """Persist one answer and award points when correct."""

        DailyQuestionService.ensure_attempt_storage(db)

        today = date.today()
        if question_date != today:
            raise ValueError("Only today's daily question can be answered.")

        existing = DailyQuestionService.get_attempt(db, user.user_id, question_date)
        if existing:
            raise ValueError("Today's daily question has already been answered.")

        _, item = DailyQuestionService.get_daily_question(target_date=question_date)
        normalized_option = selected_option.strip().upper()
        valid_options = {option.option_id for option in item.options}

        if normalized_option not in valid_options:
            raise ValueError("Selected option is invalid for today's daily question.")

        user_locked = db.scalar(
            select(AppUser).where(AppUser.user_id == user.user_id).with_for_update()
        )
        if not user_locked:
            raise ValueError("Current user does not exist.")

        is_correct = int(normalized_option == item.correct_option)
        awarded_points = DailyQuestionService.REWARD_POINTS if is_correct else 0
        points_txn_id = None

        if awarded_points:
            ledger = DailyQuestionService._append_points_ledger(
                db=db,
                user=user_locked,
                change_points=awarded_points,
                biz_type=DailyQuestionService.REWARD_BIZ_TYPE,
                biz_id=int(question_date.strftime("%Y%m%d")),
                note="Daily question answered correctly.",
            )
            points_txn_id = ledger.txn_id

        attempt = DailyQuestionAttempt(
            user_id=user.user_id,
            question_date=question_date,
            subject=item.subject,
            difficulty=item.difficulty,
            title=item.title,
            selected_option=normalized_option,
            correct_option=item.correct_option,
            is_correct=is_correct,
            awarded_points=awarded_points,
            points_txn_id=points_txn_id,
        )

        db.add(attempt)

        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ValueError("Today's daily question has already been answered.") from exc

        db.refresh(attempt)
        return attempt

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
        db.flush()
        return ledger
