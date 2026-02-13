"""Application configuration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "AURIX eBay Auto-Listing"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aurix"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/aurix"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "RS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # eBay API
    ebay_app_id: Optional[str] = None
    ebay_cert_id: Optional[str] = None
    ebay_dev_id: Optional[str] = None
    ebay_sandbox: bool = True
    ebay_oauth_url: str = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
    ebay_api_base_url: str = "https://api.sandbox.ebay.com"

    # AI / Vision (OpenAI-compatible)
    ai_api_key: Optional[str] = None
    ai_base_url: Optional[str] = None  # e.g. OpenAI or local
    ai_model: str = "gpt-4o-mini"

    # Retry
    ebay_retry_max_attempts: int = 5
    ebay_retry_backoff_base: float = 1.0
    ebay_rate_limit_delay_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
