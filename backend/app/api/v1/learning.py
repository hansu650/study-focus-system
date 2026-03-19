"""Learning endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.user import AppUser
from app.db.session import get_db
from app.schemas.learning import (
    AIChatRequest,
    AIChatResponse,
    DailyQuestionAnswerRequest,
    DailyQuestionAnswerResponse,
    DailyQuestionAttemptOut,
    DailyQuestionOptionOut,
    DailyQuestionOut,
)
from app.services.ai_service import AIService
from app.services.daily_question_service import DailyQuestionService

router = APIRouter(prefix="/learning", tags=["Learning"])


@router.get("/daily-question", response_model=DailyQuestionOut)
def get_daily_question(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
    target_date: Annotated[date | None, Query(description="Reference date, default: today")] = None,
    subject: Annotated[str | None, Query(description="Optional subject filter")] = None,
) -> DailyQuestionOut:
    """Get one daily question for study practice."""

    try:
        question_date, item = DailyQuestionService.get_daily_question(target_date=target_date, subject=subject)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    attempt = DailyQuestionService.get_attempt(db, current_user.user_id, question_date)

    return DailyQuestionOut(
        question_date=question_date,
        subject=item.subject,
        difficulty=item.difficulty,
        title=item.title,
        question=item.question,
        answer_hint=item.answer_hint,
        reward_points=DailyQuestionService.REWARD_POINTS,
        options=[DailyQuestionOptionOut(option_id=option.option_id, content=option.content) for option in item.options],
        attempt=DailyQuestionAttemptOut.model_validate(attempt) if attempt else None,
    )


@router.post("/daily-question/answer", response_model=DailyQuestionAnswerResponse, status_code=status.HTTP_201_CREATED)
def answer_daily_question(
    payload: DailyQuestionAnswerRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> DailyQuestionAnswerResponse:
    """Submit today's answer for the daily quiz."""

    try:
        attempt = DailyQuestionService.submit_answer(
            db=db,
            user=current_user,
            question_date=payload.question_date,
            selected_option=payload.selected_option,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return DailyQuestionAnswerResponse(
        question_date=attempt.question_date,
        selected_option=attempt.selected_option,
        correct_option=attempt.correct_option,
        is_correct=int(attempt.is_correct),
        awarded_points=int(attempt.awarded_points),
        answered_at=attempt.answered_at,
    )


@router.post("/ai-chat", response_model=AIChatResponse)
def ask_ai(
    payload: AIChatRequest,
    _: Annotated[AppUser, Depends(get_current_user)],
) -> AIChatResponse:
    """Ask AI learning assistant during break session."""

    system_prompt = payload.system_prompt or "You are a helpful study assistant."

    try:
        result = AIService.chat(question=payload.question, system_prompt=system_prompt)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return AIChatResponse(answer=result.answer, provider=result.provider, model=result.model)
