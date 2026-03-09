"""Redeem order schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RedeemOrderStatus(str, Enum):
    """Allowed redeem order status values."""

    CREATED = "CREATED"
    PAID = "PAID"
    VERIFIED = "VERIFIED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class RedeemOrderCreateRequest(BaseModel):
    """Request body for creating redeem order."""

    store_name: str = Field(min_length=1, max_length=120)
    points_cost: int = Field(gt=0, le=100000)
    print_quota_pages: int = Field(gt=0, le=100000)
    expire_minutes: int = Field(default=10080, ge=10, le=43200)


class RedeemOrderVerifyRequest(BaseModel):
    """Request body for merchant verify action."""

    coupon_token: str = Field(min_length=8, max_length=64)
    verifier_id: str = Field(min_length=1, max_length=64)


class RedeemOrderCancelRequest(BaseModel):
    """Request body for cancel action."""

    reason: str | None = Field(default=None, max_length=255)


class RedeemOrderOut(BaseModel):
    """Redeem order response schema."""

    model_config = ConfigDict(from_attributes=True)

    redeem_order_id: int
    order_no: str
    user_id: int
    school_id: int
    store_name: str
    points_cost: int
    print_quota_pages: int
    coupon_token: str
    qr_payload: str
    status: RedeemOrderStatus
    points_txn_id: int | None
    expire_at: datetime
    verified_at: datetime | None
    verified_by: str | None
    created_at: datetime
    updated_at: datetime


class RedeemOrderListOut(BaseModel):
    """Paginated redeem order list response."""

    page: int
    page_size: int
    total: int
    items: list[RedeemOrderOut]
