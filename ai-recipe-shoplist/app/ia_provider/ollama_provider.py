"""Ollama local LLM provider implementation."""

from typing import Dict, List

from ..config.pydantic_config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT
from ..config.logging_config import get_logger
from ..utils.retry_utils import NetworkError, create_ai_retry_config, with_ai_retry
from .base_provider import BaseAIProvider

# Get module logger
logger = get_logger(__name__)

# Ollama imports
try:
    import ollama
except ImportError:
    ollama = None


class OllamaProvider(BaseAIProvider):
    """Ollama local LLM provider with tenacity-based retry logic."""
    
    def __init__(self):
        if not ollama:
            raise ImportError("Ollama library not installed. Run: pip install ollama")
        
        self.name = "OllamaProvider"
        self.base_url = OLLAMA_HOST
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
        
        # Create tenacity-based retry configuration (local service, no rate limiting needed usually)
        self.retry_config = create_ai_retry_config("OLLAMA", requests_per_minute=0)  # 0 = no rate limiting
        
        # Test connection
        try:
            client = ollama.Client(host=self.base_url)
            client.list()
            logger.info(f"Ollama provider initialized - Model: {self.model}, Base URL: {self.base_url}")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}: {e}")
    
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation using Ollama with tenacity retry logic."""
        
        @with_ai_retry(self.retry_config)
        async def make_ollama_request():
            try:
                client = ollama.AsyncClient(host=self.base_url)
                
                # Format prompt for Ollama
                prompt = ""
                for msg in messages:
                    if msg["role"] == "system":
                        prompt += f"System: {msg['content']}\n\n"
                    elif msg["role"] == "user":
                        prompt += f"Human: {msg['content']}\n\n"
                prompt += "Assistant: "
                
                response = await client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={
                        "temperature": kwargs.get("temperature", 0.1),
                        "num_predict": kwargs.get("max_tokens", 2000),
                    }
                )
                return response['response']
            except Exception as e:
                # Convert connection errors to our retry framework
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ["connection", "timeout", "network"]):
                    raise NetworkError(f"Ollama connection error: {e}")
                else:
                    raise  # Let tenacity decide if it's retryable
        
        try:
            return await make_ollama_request()
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    # async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
    #     """Extract structured recipe data from HTML using Ollama."""
    #     return await OpenAIProvider.extract_recipe_data(self, html_content, url)
    
    # async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
    #     """Normalize ingredient texts into structured data."""
    #     return await OpenAIProvider.normalize_ingredients(self, ingredients)
    
    # async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    #     """Match and rank products for an ingredient using AI."""
    #     return await OpenAIProvider.match_products(self, ingredient, products)