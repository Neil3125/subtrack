"""Hugging Face AI provider implementation."""
from typing import Optional, Dict, Any
from app.ai.provider import AIProvider
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)


class HuggingFaceProvider(AIProvider):
    """
    Hugging Face Inference API provider.
    
    Completely free with 30,000 requests/month.
    No credit card required.
    """
    
    def __init__(
        self, 
        api_key: str,
        model: str = "meta-llama/Llama-2-7b-chat-hf",
        base_url: str = "https://router.huggingface.co/models"
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
        Generate a text completion using Hugging Face Inference API.
        
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
        # Combine system and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": full_prompt,
            "parameters": {
                "temperature": temperature,
                "max_length": max_tokens + len(full_prompt.split()),
                "top_p": 0.95,
                "repetition_penalty": 1.2,
                "do_sample": True
            }
        }
        
        try:
            logger.info(f"🤖 Calling Hugging Face API: model={self.model}, prompt_length={len(prompt)}")
            
            # Construct the proper URL
            # router.huggingface.co uses format: /models/{model_id}
            model_url = f"{self.base_url}/{self.model}" if not self.base_url.endswith("/") else f"{self.base_url}{self.model}"
            
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(
                    model_url,
                    headers=headers,
                    json=data
                )
                logger.info(f"✅ Hugging Face API response: status={response.status_code}")
                
                if response.status_code == 401:
                    logger.error("Hugging Face authentication failed (401)")
                    raise Exception(
                        "Invalid Hugging Face API key. Please check your HF_API_KEY."
                    )
                
                if response.status_code == 503:
                    logger.error("Hugging Face model loading (503)")
                    raise Exception(
                        "Model is loading. Please try again in a few seconds."
                    )
                
                response.raise_for_status()
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    # Response is a list of objects
                    if isinstance(result[0], dict) and "generated_text" in result[0]:
                        content = result[0]["generated_text"]
                        # Remove the input prompt from the output if it's there
                        if content.startswith(prompt):
                            content = content[len(prompt):].strip()
                        logger.info(f"✅ Hugging Face success: {len(content)} chars returned")
                        return content
                    elif isinstance(result[0], dict) and "summary_text" in result[0]:
                        content = result[0]["summary_text"]
                        logger.info(f"✅ Hugging Face success: {len(content)} chars returned")
                        return content
                
                # Fallback error
                raise Exception(f"Unexpected response format: {result}")
                    
        except httpx.TimeoutException:
            logger.error(f"Hugging Face request timed out after {self.timeout}s")
            raise Exception(
                f"Request timed out after {self.timeout} seconds. "
                "Please try again or enter details manually."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Hugging Face HTTP error: {e.response.status_code}")
            raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Hugging Face unexpected error: {str(e)}")
            raise Exception(f"Hugging Face error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the provider is configured with an API key."""
        return bool(self.api_key)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration."""
        return {
            "provider": "huggingface",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "free_tier": "30,000 requests/month"
        }
