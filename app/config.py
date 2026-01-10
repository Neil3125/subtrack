"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file first
load_dotenv(".env", override=True)


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:///./subtrack.db"
    
    # AI Provider (optional)
    subtrack_ai_provider: str = "gemini"  # "gemini" or "openai"
    subtrack_ai_api_key: Optional[str] = None
    subtrack_ai_model: str = "gemini-pro"  # gemini-pro for Gemini, gpt-4 for OpenAI
    subtrack_ai_base_url: str = "https://api.openai.com/v1"  # Only used for OpenAI
    
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
