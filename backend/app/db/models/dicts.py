"""Dictionary models: region, school, college."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class DictRegion(Base):
    """Region dictionary table."""

    __tablename__ = "dict_region"

    region_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    region_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    region_name: Mapped[str] = mapped_column(String(100), nullable=False)
    region_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    parent_region_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("dict_region.region_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True,
    )
    sort_no: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("100"))
    is_enabled: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class DictSchool(Base):
    """School dictionary table."""

    __tablename__ = "dict_school"

    school_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    school_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    school_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    region_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("dict_region.region_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    school_type: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("1"))
    is_enabled: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class DictCollege(Base):
    """College dictionary table."""

    __tablename__ = "dict_college"

    college_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("dict_school.school_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    college_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    college_name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_enabled: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
