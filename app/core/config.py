from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    project_name: str = "RemontHub API"
    environment: str = "development"

    # Injected by docker-compose; sensible localhost defaults for bare-metal runs.
    database_url: str = "postgresql+asyncpg://remonthub:remonthub@localhost:5433/remonthub"
    redis_url: str = "redis://localhost:6380/0"

    secret_key: str = "dev-secret-change-me-please-32chars-min"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_days: int = 30

    # NoDecode: read the raw env string, split it ourselves (comma-separated).
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3030",
        "http://localhost:3000",
    ]

    seed_on_start: bool = True
    admin_email: str = "admin@remonthub.kz"
    admin_password: str = "admin12345"

    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""

    # File uploads (product/master/etc. photos uploaded from the admin panel).
    upload_dir: str = "uploads"
    max_upload_mb: int = 8
    # Origin used to build absolute URLs for uploaded files (no trailing slash, no /api).
    public_base_url: str = "http://localhost:8000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
