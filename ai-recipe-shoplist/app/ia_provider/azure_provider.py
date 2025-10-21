"""Azure OpenAI provider implementation."""

import os
from typing import Dict, List

from ..config.logging_config import get_logger
from ..utils.retry_utils import (
    NetworkError,
    RateLimitError,
    ServerError,
    create_ai_retry_config,
    with_ai_retry,
)
from .base_provider import BaseAIProvider

# Get module logger
logger = get_logger(__name__)

# Azure OpenAI imports
try:
    import openai
except ImportError:
    openai = None


class AzureProvider(BaseAIProvider):
    """Azure OpenAI provider with tenacity-based retry logic."""
    
    def __init__(self):
        if not openai:
            raise ImportError("OpenAI library not installed. Run: pip install openai")

        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables must be set")
        
        self.name = "AzureProvider"
        self.client = openai.AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
        
        # Create tenacity-based retry configuration (Azure typically has good rate limits)
        self.retry_config = create_ai_retry_config("AZURE", requests_per_minute=120)
        
        logger.info(f"Azure OpenAI provider initialized - Deployment: {self.deployment_name}")
        logger.info(f"Retry config - Max retries: {self.retry_config.max_retries}, RPM limit: {self.retry_config.rate_limiter.requests_per_minute if self.retry_config.rate_limiter else 'None'}")
    
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation using Azure OpenAI with tenacity retry logic."""
        
        @with_ai_retry(self.retry_config)
        async def make_azure_request():
            try:
                response = await self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_tokens=kwargs.get("max_tokens", 2000),
                    temperature=kwargs.get("temperature", 0.1)
                )
                return response.choices[0].message.content
            except Exception as e:
                # Convert Azure-specific errors to our retry framework
                error_str = str(e).lower()
                if "rate limit" in error_str or "429" in error_str:
                    raise RateLimitError(f"Azure rate limit: {e}")
                elif any(keyword in error_str for keyword in ["server", "503", "502", "500"]):
                    raise ServerError(f"Azure server error: {e}")
                elif any(keyword in error_str for keyword in ["timeout", "connection"]):
                    raise NetworkError(f"Azure network error: {e}")
                else:
                    raise  # Let tenacity decide if it's retryable
        
        try:
            return await make_azure_request()
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            raise
    
    # async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
    #     """Extract structured recipe data from HTML using Azure OpenAI."""
    #     # Similar implementation to OpenAI but using Azure client
    #     return await OpenAIProvider.extract_recipe_data(self, html_content, url)
    
    # async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
    #     """Normalize ingredient texts into structured data."""
    #     return await OpenAIProvider.normalize_ingredients(self, ingredients)
    
    # async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    #     """Match and rank products for an ingredient using AI."""
    #     return await OpenAIProvider.match_products(self, ingredient, products)