"""Redeem order model."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class RedeemOrder(Base):
    """Points redeem order for print coupon."""

    __tablename__ = "redeem_order"

    redeem_order_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    school_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    store_name: Mapped[str] = mapped_column(String(120), nullable=False)
    points_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    print_quota_pages: Mapped[int] = mapped_column(Integer, nullable=False)
    coupon_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    qr_payload: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'CREATED'"))
    points_txn_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    expire_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
