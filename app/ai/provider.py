"""AI provider interface - Powered by Google Gemini."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.config import settings


# Generic AI error classes
class RateLimitError(Exception):
    """Raised when API returns 429 (rate limited)."""
    pass


class ServiceUnavailableError(Exception):
    """Raised when API returns 503 (service down)."""
    pass


class AIProviderError(Exception):
    """General AI provider error."""
    pass


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate a text completion."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available."""
        pass


class DummyAIProvider(AIProvider):
    """Dummy provider for when AI is not configured."""
    
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Return a message indicating AI is not configured."""
        return "AI provider not configured. Set SUBTRACK_AI_API_KEY to enable AI features."
    
    def is_available(self) -> bool:
        """AI is not available."""
        return False


def get_ai_provider() -> AIProvider:
    """Get the configured AI provider.

    SubTrack currently supports Google Gemini.

    This function also hardens configuration to avoid common misconfigurations
    (e.g., pointing Gemini at an OpenAI base URL, which results in HTTP 405).
    """
    if settings.subtrack_ai_api_key:
        from app.ai.gemini_provider import GeminiProvider

        base_url = (settings.subtrack_ai_base_url or "").strip()
        model = (settings.subtrack_ai_model or "").strip()

        # Guard against accidental OpenAI base URL configuration
        if "api.openai.com" in base_url or base_url.rstrip("/").endswith("/v1"):
            base_url = "https://generativelanguage.googleapis.com/v1beta"

        # Guard against empty or clearly non-Gemini (OpenAI) model names.
        # (HTTP 405 issues are typically caused by the wrong base URL, not the model.)
        if not model or model.lower().startswith("gpt-"):
            model = "gemini-2.0-flash"

        return GeminiProvider(
            api_key=settings.subtrack_ai_api_key,
            model=model,
            base_url=base_url,
        )

    return DummyAIProvider()
