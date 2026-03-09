"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfileOut(BaseModel):
    """Current user profile response."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    nickname: str
    email: EmailStr | None
    phone: str | None
    student_no: str | None
    grade_year: int | None
    major_name: str | None
    region_id: int
    school_id: int
    college_id: int
    total_points: int
    total_focus_minutes: int
    created_at: datetime


class UserUpdateRequest(BaseModel):
    """Editable user profile fields."""

    nickname: str | None = Field(default=None, min_length=1, max_length=60)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=6, max_length=20)
    avatar_url: str | None = Field(default=None, max_length=255)
    major_name: str | None = Field(default=None, max_length=100)
    grade_year: int | None = Field(default=None, ge=2000, le=2100)
