"""Daily question attempt model."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, SmallInteger, String, UniqueConstraint, text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


MYSQL_UNSIGNED_BIGINT = Integer().with_variant(mysql.BIGINT(unsigned=True), "mysql")
MYSQL_PK_BIGINT = Integer().with_variant(mysql.BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")


class DailyQuestionAttempt(Base):
    """Persist one user's daily quiz submission."""

    __tablename__ = "daily_question_attempt"
    __table_args__ = (
        UniqueConstraint("user_id", "question_date", name="uk_question_attempt_user_date"),
        Index("idx_question_attempt_answered", "answered_at"),
    )

    attempt_id: Mapped[int] = mapped_column(
        MYSQL_PK_BIGINT,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        MYSQL_UNSIGNED_BIGINT,
        ForeignKey("app_user.user_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    question_date: Mapped[date] = mapped_column(Date, nullable=False)
    subject: Mapped[str] = mapped_column(String(64), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    selected_option: Mapped[str] = mapped_column(String(1), nullable=False)
    correct_option: Mapped[str] = mapped_column(String(1), nullable=False)
    is_correct: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))
    awarded_points: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    points_txn_id: Mapped[int | None] = mapped_column(
        MYSQL_UNSIGNED_BIGINT,
        ForeignKey("point_ledger.txn_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    answered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
