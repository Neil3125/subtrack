"""Groq AI provider implementation."""
from typing import Optional, Dict, Any
from app.ai.provider import AIProvider
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)


class GroqProvider(AIProvider):
    """
    Groq API provider.
    
    Completely free with unlimited requests.
    Fastest LLM inference available.
    No credit card required.
    """
    
    def __init__(
        self, 
        api_key: str,
        model: str = "mixtral-8x7b-32768",
        base_url: str = "https://api.groq.com/openai/v1"
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
        Generate a text completion using Groq API.
        
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
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            logger.info(f"🤖 Calling Groq API: model={self.model}, prompt_length={len(prompt)}")
            
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                logger.info(f"✅ Groq API response: status={response.status_code}")
                
                if response.status_code == 401:
                    logger.error("Groq authentication failed (401)")
                    raise Exception(
                        "Invalid Groq API key. Please check your GROQ_API_KEY."
                    )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract the response content
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    logger.info(f"✅ Groq success: {len(content)} chars returned")
                    return content
                else:
                    raise Exception(f"Unexpected response format: {result}")
                    
        except httpx.TimeoutException:
            logger.error(f"Groq request timed out after {self.timeout}s")
            raise Exception(
                f"Request timed out after {self.timeout} seconds. "
                "Please try again or enter details manually."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Groq HTTP error: {e.response.status_code}")
            raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Groq unexpected error: {str(e)}")
            raise Exception(f"Groq error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the provider is configured with an API key."""
        return bool(self.api_key)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": "groq",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "free_tier": "Unlimited requests"
        }
