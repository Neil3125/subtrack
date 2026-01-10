"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file first
load_dotenv(".env", override=True)


def get_database_url() -> str:
    """
    Get database URL with Railway PostgreSQL support.
    
    Railway provides DATABASE_URL for PostgreSQL services.
    This ensures data persists across code deployments - you only need to
    set up PostgreSQL once on Railway and your data is safe forever.
    """
    # Check Railway's DATABASE_URL first (PostgreSQL)
    url = os.environ.get("DATABASE_URL")
    if url:
        # Railway PostgreSQL URLs start with postgres:// but SQLAlchemy needs postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    
    # Fall back to explicit database_url setting
    return os.environ.get("database_url", "sqlite:///./subtrack.db")


class Settings(BaseSettings):
    """Application settings."""
    
    # Database - automatically uses Railway PostgreSQL if available
    database_url: str = get_database_url()
    
    # AI Provider - Google Gemini (free tier available)
    subtrack_ai_provider: str = "gemini"
    subtrack_ai_api_key: Optional[str] = "AIzaSyCNiWJ2ZPqmGcQRR9UAXeyTPRseOm00QSM"
    subtrack_ai_model: str = "gemma-3-27b-it"
    subtrack_ai_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    
    # AI Cache Settings
    ai_cache_ttl: int = 86400  # 24 hours in seconds
    ai_request_timeout: int = 30  # seconds
    ai_max_retries: int = 2
    ai_daily_limit: int = 1000  # Daily request limit (GitHub Models: unlimited)
    
    # App
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
