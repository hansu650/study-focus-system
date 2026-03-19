"""Learning feature schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class DailyQuestionOptionOut(BaseModel):
    """One selectable option for the daily quiz."""

    option_id: str
    content: str


class DailyQuestionAttemptOut(BaseModel):
    """Persisted answer state for today's quiz."""

    model_config = ConfigDict(from_attributes=True)

    question_date: date
    selected_option: str
    correct_option: str
    is_correct: int
    awarded_points: int
    answered_at: datetime


class DailyQuestionOut(BaseModel):
    """Daily question response."""

    question_date: date
    subject: str
    difficulty: str
    title: str
    question: str
    answer_hint: str
    reward_points: int
    options: list[DailyQuestionOptionOut]
    attempt: DailyQuestionAttemptOut | None = None


class DailyQuestionAnswerRequest(BaseModel):
    """Answer submission for today's quiz."""

    question_date: date
    selected_option: str = Field(min_length=1, max_length=1)


class DailyQuestionAnswerResponse(BaseModel):
    """Submission result for today's quiz."""

    question_date: date
    selected_option: str
    correct_option: str
    is_correct: int
    awarded_points: int
    answered_at: datetime


class AIChatRequest(BaseModel):
    """AI chat request body."""

    question: str = Field(min_length=1, max_length=2000)
    system_prompt: str | None = Field(default=None, min_length=1, max_length=500)


class AIChatResponse(BaseModel):
    """AI chat response body."""

    answer: str
    provider: str
    model: str
