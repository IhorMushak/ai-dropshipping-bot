"""
Application configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    # Application
    PROJECT_NAME: str = "AI Dropshipping Bot"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/dropshipping")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    
    # External APIs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ALIEXPRESS_API_KEY: str = os.getenv("ALIEXPRESS_API_KEY", "")
    AMAZON_API_KEY: str = os.getenv("AMAZON_API_KEY", "")
    
    # PayPal
    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    PAYPAL_ENVIRONMENT: str = os.getenv("PAYPAL_ENVIRONMENT", "sandbox")
    
    # SEO (Medium, Pinterest)
    MEDIUM_TOKEN: str = os.getenv("MEDIUM_TOKEN", "")
    PINTEREST_TOKEN: str = os.getenv("PINTEREST_TOKEN", "")
    
    # InfluenceFlow
    INFLUENCEFLOW_API_KEY: str = os.getenv("INFLUENCEFLOW_API_KEY", "")
    INFLUENCEFLOW_API_URL: str = os.getenv("INFLUENCEFLOW_API_URL", "https://api.influenceflow.com/v1")
    
    # CORS - Allow all origins for production
    CORS_ORIGINS: list = ["*"]


settings = Settings()
