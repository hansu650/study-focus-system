"""Project settings module.

This module loads environment variables and exposes derived values such as
Database URL and CORS origin list.
"""

from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from `.env` and OS environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    app_name: str = Field(default="Study Focus API", description="Service name")
    debug: bool = Field(default=False, description="Enable debug mode")
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")

    # JWT settings
    secret_key: str = Field(default="CHANGE_ME", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=120, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")

    # CORS settings: comma-separated origins or "*"
    cors_allow_origins: str = Field(default="*", alias="CORS_ALLOW_ORIGINS")

    # MySQL settings
    mysql_host: str = Field(default="127.0.0.1", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="root", alias="MYSQL_USER")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")
    mysql_db: str = Field(default="study_focus", alias="MYSQL_DB")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # AI provider settings
    ai_provider: str = Field(default="openai_compatible", alias="AI_PROVIDER")
    ai_api_base: str = Field(default="", alias="AI_API_BASE")
    ai_api_key: str = Field(default="", alias="AI_API_KEY")
    anthropic_auth_token: str = Field(default="", alias="ANTHROPIC_AUTH_TOKEN")
    ai_model: str = Field(default="gpt-4o-mini", alias="AI_MODEL")

    @property
    def database_url(self) -> str:
        """Build SQLAlchemy database URL for MySQL."""

        safe_password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{self.mysql_user}:{safe_password}@"
            f"{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins into a list."""

        if self.cors_allow_origins.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.cors_allow_origins.split(",") if item.strip()]

    @property
    def resolved_ai_api_key(self) -> str:
        """Return AI key with fallback to Anthropic token variable."""

        return (self.ai_api_key or self.anthropic_auth_token or "").strip()


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton settings object."""

    return Settings()


settings = get_settings()
