"""Learning feature schemas."""

from datetime import date

from pydantic import BaseModel, Field


class DailyQuestionOut(BaseModel):
    """Daily question response."""

    question_date: date
    subject: str
    difficulty: str
    title: str
    question: str
    answer_hint: str


class AIChatRequest(BaseModel):
    """AI chat request body."""

    question: str = Field(min_length=1, max_length=2000)
    system_prompt: str | None = Field(default=None, min_length=1, max_length=500)


class AIChatResponse(BaseModel):
    """AI chat response body."""

    answer: str
    provider: str
    model: str
