"""Anthropic Claude AI provider implementation."""
from typing import Optional, Dict, Any
from app.ai.provider import AIProvider
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    """
    Anthropic Claude API provider.
    
    Uses the Anthropic API for Claude models.
    Free tier available with pay-as-you-go pricing.
    """
    
    def __init__(
        self, 
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        base_url: str = "https://api.anthropic.com/v1"
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
        Generate a text completion using Claude API.
        
        Args:
            prompt: The user's prompt/question
            system_prompt: Optional system instructions
            temperature: Creativity setting (0-1)
            max_tokens: Maximum response length
            
        Returns:
            The generated text response
            
        Raises:
            Exception: For API errors
        """
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        if system_prompt:
            data["system"] = system_prompt
        
        try:
            logger.info(f"🤖 Calling Claude API: model={self.model}, prompt_length={len(prompt)}")
            
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=data
                )
                logger.info(f"✅ Claude API response: status={response.status_code}")
                
                if response.status_code == 401:
                    logger.error("Claude authentication failed (401)")
                    raise Exception(
                        "Invalid Anthropic API key. Please check your SUBTRACK_AI_API_KEY."
                    )
                
                if response.status_code == 429:
                    logger.error("Claude rate limit (429)")
                    raise Exception(
                        "Rate limit reached. Please try again later."
                    )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract the response content
                if "content" in result and len(result["content"]) > 0:
                    content = result["content"][0]["text"]
                    logger.info(f"✅ Claude success: {len(content)} chars returned")
                    return content
                else:
                    raise Exception(f"Unexpected response format: {result}")
                    
        except httpx.TimeoutException:
            logger.error(f"Claude request timed out after {self.timeout}s")
            raise Exception(
                f"Request timed out after {self.timeout} seconds. "
                "Please try again or enter details manually."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Claude HTTP error: {e.response.status_code}")
            error_text = e.response.text
            logger.error(f"Error details: {error_text}")
            raise Exception(f"Claude error: {error_text}")
        except Exception as e:
            logger.error(f"Claude unexpected error: {str(e)}")
            raise Exception(f"Claude error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the provider is configured with an API key."""
        return bool(self.api_key)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": "anthropic",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "pricing": "Pay as you go (very cheap)"
        }
