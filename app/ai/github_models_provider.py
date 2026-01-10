"""GitHub Models AI provider implementation."""
from typing import Optional, Dict, Any
from app.ai.provider import AIProvider
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)


class GitHubModelsProvider(AIProvider):
    """
    GitHub Models API provider.
    
    Uses the GitHub Models API for free access to various AI models
    including OpenAI GPT-4, Llama, Mistral, and more.
    Completely free with GitHub authentication.
    """
    
    def __init__(
        self, 
        api_key: str,
        model: str = "gpt-4o",
        base_url: str = "https://models.github.ai/inference"
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
        Generate a text completion using GitHub Models API.
        
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            logger.info(f"🤖 Calling GitHub Models API: model={self.model}, prompt_length={len(prompt)}")
            
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                logger.info(f"✅ GitHub Models API response: status={response.status_code}")
                
                if response.status_code == 401:
                    logger.error("GitHub Models authentication failed (401)")
                    raise Exception(
                        "Invalid GitHub token. Please check your SUBTRACK_AI_API_KEY."
                    )
                
                if response.status_code == 429:
                    logger.error("GitHub Models rate limit (429)")
                    raise Exception(
                        "Rate limit reached. Please try again later."
                    )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract the response content
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    logger.info(f"✅ GitHub Models success: {len(content)} chars returned")
                    return content
                else:
                    raise Exception(f"Unexpected response format: {result}")
                    
        except httpx.TimeoutException:
            logger.error(f"GitHub Models request timed out after {self.timeout}s")
            raise Exception(
                f"Request timed out after {self.timeout} seconds. "
                "Please try again or enter details manually."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub Models HTTP error: {e.response.status_code}")
            error_text = e.response.text
            logger.error(f"Error details: {error_text}")
            raise Exception(f"GitHub Models error: {error_text}")
        except Exception as e:
            logger.error(f"GitHub Models unexpected error: {str(e)}")
            raise Exception(f"GitHub Models error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the provider is configured with an API key."""
        return bool(self.api_key)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": "github_models",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "pricing": "Free (GitHub token required)"
        }
