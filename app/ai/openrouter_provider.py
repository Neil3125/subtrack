"""OpenRouter AI provider implementation."""
from typing import Optional, Dict, Any
from app.ai.provider import AIProvider
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when API returns 429 (rate limited)."""
    pass


class ServiceUnavailableError(Exception):
    """Raised when API returns 503 (service down)."""
    pass


class AIProviderError(Exception):
    """General AI provider error."""
    pass


class OpenRouterProvider(AIProvider):
    """
    OpenRouter AI provider using the OpenAI-compatible API.
    
    OpenRouter provides access to various AI models including free tiers.
    Uses the standard OpenAI chat completions API format.
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "google/gemini-2.0-flash-001:free",
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = settings.ai_request_timeout
        
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate a text completion using OpenRouter's API.
        
        Args:
            prompt: The user's prompt/question
            system_prompt: Optional system instructions
            temperature: Creativity setting (0-1)
            max_tokens: Maximum response length
            
        Returns:
            The generated text response
            
        Raises:
            RateLimitError: When daily limit (50 requests) is exceeded
            ServiceUnavailableError: When OpenRouter is down
            AIProviderError: For other API errors
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://subtrack.app",  # Required by OpenRouter
            "X-Title": "SubTrack Subscription Manager"  # Optional but recommended
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                # Handle specific error codes
                if response.status_code == 429:
                    logger.warning("OpenRouter rate limit reached (429)")
                    raise RateLimitError(
                        "Daily request limit reached (50 requests/day on free tier). "
                        "AI features will be available again tomorrow."
                    )
                
                if response.status_code == 503:
                    logger.error("OpenRouter service unavailable (503)")
                    raise ServiceUnavailableError(
                        "OpenRouter service is temporarily unavailable. "
                        "Please try again in a few minutes."
                    )
                
                if response.status_code == 401:
                    logger.error("OpenRouter authentication failed (401)")
                    raise AIProviderError(
                        "Invalid API key. Please check your SUBTRACK_AI_API_KEY."
                    )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract the response content
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    logger.debug(f"OpenRouter response received: {len(content)} chars")
                    return content
                else:
                    raise AIProviderError("Invalid response format from OpenRouter")
                    
        except httpx.TimeoutException:
            logger.error(f"OpenRouter request timed out after {self.timeout}s")
            raise AIProviderError(
                f"Request timed out after {self.timeout} seconds. "
                "Please try again or enter details manually."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter HTTP error: {e.response.status_code}")
            raise AIProviderError(f"HTTP error: {e.response.status_code}")
        except (RateLimitError, ServiceUnavailableError, AIProviderError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"OpenRouter unexpected error: {str(e)}")
            raise AIProviderError(f"Unexpected error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the provider is configured with an API key."""
        return bool(self.api_key)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": "openrouter",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "daily_limit": settings.ai_daily_limit
        }
