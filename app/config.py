"""Anwendungs-Konfiguration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Konfiguration aus Umgebungsvariablen."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AURIX Backend"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aurix"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # eBay API
    ebay_app_id: Optional[str] = None
    ebay_cert_id: Optional[str] = None
    ebay_dev_id: Optional[str] = None
    ebay_oauth_url: str = "https://api.ebay.com/identity/v1/oauth2/token"
    ebay_api_base_url: str = "https://api.ebay.com"
    ebay_sandbox: bool = True

    # OpenAI / Vision
    openai_api_key: Optional[str] = None

    # Retry
    ebay_retry_max_attempts: int = 5
    ebay_retry_backoff_factor: float = 2.0


@lru_cache
def get_settings() -> Settings:
    """Cached Settings-Instanz."""
    return Settings()
