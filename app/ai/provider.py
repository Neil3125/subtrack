"""AI provider interface and implementations."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.config import settings
import httpx
import json
import os


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


class OpenAIProvider(AIProvider):
    """OpenAI-compatible API provider."""
    
    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip('/')
        
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate a text completion using OpenAI API."""
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
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"AI API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the provider is configured."""
        return bool(self.api_key)


class GeminiProvider(AIProvider):
    """Google Gemini AI provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Generate a text completion using Gemini API."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel(self.model)
            
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Generate response
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            
            return response.text
        except ImportError:
            raise Exception("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the provider is configured."""
        return bool(self.api_key)


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
    """Get the configured AI provider."""
    if settings.subtrack_ai_api_key:
        provider_type = settings.subtrack_ai_provider.lower()
        
        if provider_type == "gemini":
            return GeminiProvider(
                api_key=settings.subtrack_ai_api_key,
                model=settings.subtrack_ai_model
            )
        elif provider_type == "openai":
            return OpenAIProvider(
                api_key=settings.subtrack_ai_api_key,
                model=settings.subtrack_ai_model,
                base_url=settings.subtrack_ai_base_url
            )
        else:
            # Default to Gemini if provider not recognized
            return GeminiProvider(
                api_key=settings.subtrack_ai_api_key,
                model=settings.subtrack_ai_model
            )
    return DummyAIProvider()
