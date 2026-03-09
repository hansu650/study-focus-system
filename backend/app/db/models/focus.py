"""Focus session model."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Integer, JSON, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class FocusSession(Base):
    """Pomodoro focus session table."""

    __tablename__ = "focus_session"

    session_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    focus_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    actual_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'RUNNING'"))
    lock_mode: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'APP_BLOCK'"))
    blocked_apps_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    blocked_sites_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    interrupt_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))
    awarded_points: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    settle_status: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
