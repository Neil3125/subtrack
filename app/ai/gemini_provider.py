"""Google Gemini AI provider implementation using REST API."""
from typing import Optional, Dict, Any
from app.ai.provider import AIProvider, RateLimitError, ServiceUnavailableError, AIProviderError
from app.config import settings
import httpx
import logging
import json
import re
import asyncio

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Google AI Studio (Gemini) API provider.
    
    Uses the REST API directly for maximum compatibility.
    Free tier includes generous limits for Gemini models.
    """
    
    def __init__(
        self, 
        api_key: str,
        model: str = "gemini-2.0-flash",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = settings.ai_request_timeout
        self._retry_delay = 2  # seconds between retries
        self._max_retries = 3
        
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate a text completion using Google Gemini API.
        
        Args:
            prompt: The user's prompt/question
            system_prompt: Optional system instructions
            temperature: Creativity setting (0-1)
            max_tokens: Maximum response length
            
        Returns:
            The generated text response
            
        Raises:
            RateLimitError: When rate limit is exceeded
            ServiceUnavailableError: When API is down
            AIProviderError: For other API errors
        """
        endpoint = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        # Build the prompt - combine system prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        # Retry logic for rate limits
        last_error = None
        for attempt in range(self._max_retries):
            try:
                logger.info(f"🤖 Calling Gemini API: model={self.model}, prompt_length={len(prompt)}, attempt={attempt+1}")
                
                async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                    response = await client.post(endpoint, json=data)
                    logger.info(f"Gemini API response: status={response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Extract text from response
                        if "candidates" in result and len(result["candidates"]) > 0:
                            candidate = result["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                text = candidate["content"]["parts"][0].get("text", "")
                                logger.info(f"✅ Gemini success: {len(text)} chars returned")
                                return text
                        
                        # Check for blocked content
                        if "promptFeedback" in result:
                            feedback = result["promptFeedback"]
                            if feedback.get("blockReason"):
                                raise AIProviderError(f"Content blocked: {feedback.get('blockReason')}")
                        
                        raise AIProviderError(f"Unexpected response format: {result}")
                    
                    elif response.status_code == 429:
                        # Rate limit - wait and retry
                        error_data = response.json().get("error", {})
                        retry_info = None
                        for detail in error_data.get("details", []):
                            if detail.get("@type", "").endswith("RetryInfo"):
                                retry_delay_str = detail.get("retryDelay", "15s")
                                retry_info = int(re.search(r'\d+', retry_delay_str).group()) if re.search(r'\d+', retry_delay_str) else 15
                                break
                        
                        wait_time = retry_info or (self._retry_delay * (attempt + 1))
                        logger.warning(f"Gemini rate limit (429), waiting {wait_time}s before retry...")
                        
                        if attempt < self._max_retries - 1:
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise RateLimitError(
                                f"Rate limit exceeded. Please wait {wait_time} seconds and try again."
                            )
                    
                    elif response.status_code == 503:
                        logger.error("Gemini service unavailable (503)")
                        raise ServiceUnavailableError(
                            "Google AI service is temporarily unavailable. Please try again later."
                        )
                    
                    elif response.status_code == 400:
                        error_data = response.json().get("error", {})
                        raise AIProviderError(f"Bad request: {error_data.get('message', 'Unknown error')}")
                    
                    elif response.status_code == 401 or response.status_code == 403:
                        logger.error(f"Gemini authentication failed ({response.status_code})")
                        raise AIProviderError(
                            "Invalid API key. Please check your SUBTRACK_AI_API_KEY."
                        )
                    
                    else:
                        response.raise_for_status()
                        
            except httpx.TimeoutException:
                logger.error(f"Gemini request timed out after {self.timeout}s")
                last_error = AIProviderError(
                    f"Request timed out after {self.timeout} seconds. Please try again."
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay)
                    continue
                raise last_error
                
            except (RateLimitError, ServiceUnavailableError, AIProviderError):
                raise
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Gemini HTTP error: {e.response.status_code}")
                raise AIProviderError(f"HTTP error: {e.response.status_code}")
                
            except Exception as e:
                logger.error(f"Gemini unexpected error: {str(e)}")
                last_error = AIProviderError(f"Unexpected error: {str(e)}")
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay)
                    continue
                raise last_error
        
        raise last_error or AIProviderError("Failed after all retries")
    
    def is_available(self) -> bool:
        """Check if the provider is configured with an API key."""
        return bool(self.api_key)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": "gemini",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "pricing": "Free tier available"
        }


def parse_json_from_response(response: str) -> Dict[str, Any]:
    """
    Parse JSON from Gemini response, handling markdown code blocks.
    
    Args:
        response: Raw response text from Gemini
        
    Returns:
        Parsed dictionary or empty dict on failure
    """
    try:
        # Try direct parse first
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object in response
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    return {}
