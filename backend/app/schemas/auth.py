"""Authentication schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Register request body."""

    username: str = Field(min_length=3, max_length=50, description="Login username")
    password: str = Field(min_length=8, max_length=64, description="Login password")
    nickname: str = Field(min_length=1, max_length=60, description="Display name")
    email: EmailStr | None = Field(default=None, description="Email")
    phone: str | None = Field(default=None, min_length=6, max_length=20, description="Phone")
    student_no: str | None = Field(default=None, max_length=64, description="Student number")
    grade_year: int | None = Field(default=None, ge=2000, le=2100, description="Grade year")
    major_name: str | None = Field(default=None, max_length=100, description="Major")
    region_id: int = Field(gt=0, description="Region id")
    school_id: int = Field(gt=0, description="School id")
    college_id: int = Field(gt=0, description="College id")

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip()


class LoginRequest(BaseModel):
    """Login request body."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=64)


class TokenResponse(BaseModel):
    """Access token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token remaining seconds")


class RegisterResponse(BaseModel):
    """Register response."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    nickname: str
