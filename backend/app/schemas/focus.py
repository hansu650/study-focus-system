"""Focus session schemas."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FocusSessionStatus(str, Enum):
    """Allowed focus session status values."""

    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    INTERRUPTED = "INTERRUPTED"
    ABANDONED = "ABANDONED"


class LockMode(str, Enum):
    """Allowed lock mode values."""

    APP_BLOCK = "APP_BLOCK"
    WEB_BLOCK = "WEB_BLOCK"
    FULL_LOCK = "FULL_LOCK"
    NONE = "NONE"


class FocusSessionStartRequest(BaseModel):
    """Request body for creating a focus session."""

    planned_minutes: int = Field(ge=1, le=240)
    lock_mode: LockMode = LockMode.APP_BLOCK
    blocked_apps: list[str] | None = None
    blocked_sites: list[str] | None = None
    remark: str | None = Field(default=None, max_length=255)


class FocusSessionCompleteRequest(BaseModel):
    """Request body for completing a running session."""

    actual_minutes: int | None = Field(default=None, ge=1, le=240)
    remark: str | None = Field(default=None, max_length=255)


class FocusSessionStopRequest(BaseModel):
    """Request body for interrupting or abandoning a session."""

    actual_minutes: int | None = Field(default=None, ge=0, le=240)
    remark: str | None = Field(default=None, max_length=255)


class FocusSessionOut(BaseModel):
    """Focus session response schema."""

    model_config = ConfigDict(from_attributes=True)

    session_id: int
    user_id: int
    focus_date: date
    planned_minutes: int
    actual_minutes: int
    start_at: datetime
    end_at: datetime | None
    status: FocusSessionStatus
    lock_mode: LockMode
    blocked_apps_json: list[str] | None
    blocked_sites_json: list[str] | None
    interrupt_count: int
    awarded_points: int
    settle_status: int
    remark: str | None
    created_at: datetime
    updated_at: datetime


class FocusSessionListOut(BaseModel):
    """Paginated list result for sessions."""

    page: int
    page_size: int
    total: int
    items: list[FocusSessionOut]
