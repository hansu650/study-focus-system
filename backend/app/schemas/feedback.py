"""Feedback schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCategory(str, Enum):
    """Supported feedback categories."""

    GENERAL = "GENERAL"
    UI = "UI"
    FOCUS = "FOCUS"
    REDEEM = "REDEEM"
    DESKTOP = "DESKTOP"
    BUG = "BUG"
    IDEA = "IDEA"


class FeedbackStatus(str, Enum):
    """Lifecycle state for a feedback message."""

    NEW = "NEW"
    REVIEWED = "REVIEWED"


class FeedbackCreateRequest(BaseModel):
    """Create one feedback message."""

    category: FeedbackCategory = FeedbackCategory.GENERAL
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=5, max_length=1000)
    contact_email: str | None = Field(default=None, max_length=120)


class FeedbackOut(BaseModel):
    """Feedback response payload."""

    model_config = ConfigDict(from_attributes=True)

    feedback_id: int
    user_id: int
    category: FeedbackCategory
    title: str
    content: str
    contact_email: str | None
    status: FeedbackStatus
    created_at: datetime
    updated_at: datetime


class FeedbackListOut(BaseModel):
    """Paginated feedback list response."""

    page: int
    page_size: int
    total: int
    items: list[FeedbackOut]