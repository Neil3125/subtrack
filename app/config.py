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
    
    # AI Provider (optional)
    # Supported providers: "github_models" (free), "anthropic" (Claude - cheap), "groq", "huggingface", "openrouter", "gemini", "openai"
    subtrack_ai_provider: str = "github_models"
    subtrack_ai_api_key: Optional[str] = None
    subtrack_ai_model: str = "gpt-4o"
    subtrack_ai_base_url: str = "https://models.github.ai/inference"
    
    # AI Cache Settings
    ai_cache_ttl: int = 86400  # 24 hours in seconds
    ai_request_timeout: int = 30  # seconds
    ai_max_retries: int = 2
    ai_daily_limit: int = 50  # OpenRouter free tier daily limit
    
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
