# backend/app/config.py

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Core
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    secret_key: str = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Dropshipping Bot"
    version: str = "1.0.0"

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://admin:password@localhost:5432/dropship",
        alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # OpenAI
    openai_api_key: str = Field(default="sk-placeholder-key", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")

    # Shopify
    shopify_store_url: str = Field(default="test-store.myshopify.com", alias="SHOPIFY_STORE_URL")
    shopify_access_token: str = Field(default="shpat_test_token", alias="SHOPIFY_ACCESS_TOKEN")
    shopify_api_version: str = Field(default="2024-01", alias="SHOPIFY_API_VERSION")

    # Meta Ads
    meta_ads_access_token: str = Field(default="test_token", alias="META_ADS_ACCESS_TOKEN")
    meta_ads_ad_account_id: str = Field(default="act_test", alias="META_ADS_AD_ACCOUNT_ID")
    meta_ads_pixel_id: Optional[str] = Field(default=None, alias="META_ADS_PIXEL_ID")

    # AliExpress
    aliexpress_app_key: str = Field(default="test_key", alias="ALIEXPRESS_APP_KEY")
    aliexpress_app_secret: str = Field(default="test_secret", alias="ALIEXPRESS_APP_SECRET")
    aliexpress_tracking_id: Optional[str] = Field(default=None, alias="ALIEXPRESS_TRACKING_ID")

    # Image Generation
    flux_api_key: Optional[str] = Field(default=None, alias="FLUX_API_KEY")
    midjourney_api_key: Optional[str] = Field(default=None, alias="MIDJOURNEY_API_KEY")

    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")

    # Performance
    max_workers: int = Field(default=4, alias="MAX_WORKERS")
    rate_limit_per_minute: int = Field(default=100, alias="RATE_LIMIT_PER_MINUTE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ігноруємо додаткові поля


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency injection for settings"""
    return settings
