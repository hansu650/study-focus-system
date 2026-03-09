"""User model."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class AppUser(Base):
    """Application user table."""

    __tablename__ = "app_user"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    nickname: Mapped[str] = mapped_column(String(60), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    student_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    grade_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    major_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    school_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    college_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_focus_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("1"))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
