"""Daily question service."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyQuestion:
    """Question record for daily push."""

    subject: str
    difficulty: str
    title: str
    question: str
    answer_hint: str


class DailyQuestionService:
    """Serve deterministic daily question from local question bank."""

    QUESTION_BANK: tuple[DailyQuestion, ...] = (
        DailyQuestion(
            subject="Computer Science",
            difficulty="Easy",
            title="Time Complexity",
            question="What is the time complexity of binary search on a sorted array and why?",
            answer_hint="Think about dividing the search space by half each step.",
        ),
        DailyQuestion(
            subject="Mathematics",
            difficulty="Medium",
            title="Derivative Basics",
            question="Find the derivative of f(x)=x^3-4x+2 and evaluate it at x=2.",
            answer_hint="Use power rule term by term first, then substitute x=2.",
        ),
        DailyQuestion(
            subject="Physics",
            difficulty="Medium",
            title="Kinematics",
            question="A body starts from rest and accelerates at 2 m/s^2 for 5 s. What distance does it travel?",
            answer_hint="Use s = ut + 1/2*a*t^2 with u=0.",
        ),
        DailyQuestion(
            subject="English",
            difficulty="Easy",
            title="Grammar",
            question="Rewrite this sentence in passive voice: 'The team finished the project yesterday.'",
            answer_hint="Move object to subject position and use past passive form.",
        ),
        DailyQuestion(
            subject="Computer Science",
            difficulty="Hard",
            title="Database Index",
            question="When can adding an index slow down a system, and how would you decide whether to keep it?",
            answer_hint="Consider write amplification, selectivity, and query patterns.",
        ),
    )

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
