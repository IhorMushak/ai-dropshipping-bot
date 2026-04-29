"""
Application configuration using python-dotenv
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "AI Dropshipping Bot"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/dropshipping"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    
    # External APIs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ALIEXPRESS_API_KEY: str = os.getenv("ALIEXPRESS_API_KEY", "")
    AMAZON_API_KEY: str = os.getenv("AMAZON_API_KEY", "")
    
    # Medusa
    MEDUSA_URL: str = os.getenv("MEDUSA_URL", "http://localhost:9000")
    MEDUSA_ADMIN_TOKEN: str = os.getenv("MEDUSA_ADMIN_TOKEN", "")
    
    # Landing
    LANDING_BASE_URL: str = os.getenv("LANDING_BASE_URL", "http://localhost:8000")
    LANDING_STORAGE_PATH: str = os.getenv("LANDING_STORAGE_PATH", "/tmp/landings")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHANNEL_ID: str = os.getenv("TELEGRAM_CHANNEL_ID", "")
    
    # PayPal
    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    PAYPAL_ENVIRONMENT: str = os.getenv("PAYPAL_ENVIRONMENT", "sandbox")
    
    # SEO
    MEDIUM_TOKEN: str = os.getenv("MEDIUM_TOKEN", "")
    PINTEREST_TOKEN: str = os.getenv("PINTEREST_TOKEN", "")
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    @property
    def ALLOWED_HOSTS(self) -> list:
        return ["*"]


settings = Settings()
