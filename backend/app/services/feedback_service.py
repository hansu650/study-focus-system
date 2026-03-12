"""Feedback business service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.feedback import FeedbackMessage
from app.db.models.user import AppUser
from app.schemas.feedback import FeedbackCreateRequest


class FeedbackService:
    """Store and query user feedback messages."""

    @staticmethod
    def create_feedback(db: Session, user: AppUser, payload: FeedbackCreateRequest) -> FeedbackMessage:
        """Create one feedback message for the current user."""

        title = payload.title.strip()
        content = payload.content.strip()
        contact_email = payload.contact_email.strip() if payload.contact_email else None

        if not title:
            raise ValueError("Feedback title cannot be empty.")

        if len(content) < 5:
            raise ValueError("Feedback content must be at least 5 characters.")

        feedback = FeedbackMessage(
            user_id=user.user_id,
            category=payload.category.value,
            title=title,
            content=content,
            contact_email=contact_email or None,
            status="NEW",
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def list_my_feedback(
        db: Session,
        user_id: int,
        page: int,
        page_size: int,
    ) -> tuple[int, list[FeedbackMessage]]:
        """List recent feedback for one user."""

        query = select(FeedbackMessage).where(FeedbackMessage.user_id == user_id)
        total = int(db.scalar(select(func.count()).select_from(query.subquery())) or 0)
        rows = list(
            db.scalars(
                query.order_by(FeedbackMessage.created_at.desc(), FeedbackMessage.feedback_id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return total, rows