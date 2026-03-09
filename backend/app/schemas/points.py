"""Point ledger schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PointBalanceOut(BaseModel):
    """Current point and focus totals for current user."""

    user_id: int
    total_points: int
    total_focus_minutes: int


class PointLedgerOut(BaseModel):
    """Single point transaction response item."""

    model_config = ConfigDict(from_attributes=True)

    txn_id: int
    user_id: int
    change_points: int
    balance_before: int
    balance_after: int
    biz_type: str
    biz_id: int | None
    occurred_at: datetime
    note: str | None
    created_at: datetime


class PointLedgerListOut(BaseModel):
    """Paginated list result for point ledger."""

    page: int
    page_size: int
    total: int
    items: list[PointLedgerOut]
