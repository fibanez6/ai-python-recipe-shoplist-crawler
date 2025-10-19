"""GitHub Models provider implementation."""

import logging
import os
from typing import Any, Dict, List

from ..config.logging_config import get_logger, log_function_call
from ..utils.retry_utils import (
    HTTPRetryClient,
    create_ai_retry_config,
)
from .base_provider import BaseAIProvider
from .openai_provider import OpenAIProvider

# Get module logger
logger = get_logger(__name__)


class GitHubProvider(BaseAIProvider):
    """GitHub Models provider with tenacity-based retry logic."""
    
    def __init__(self):
        logger.debug("Initializing GitHub Models provider...")
        
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
        
        self.token = token
        self.model = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
        self.api_url = os.getenv("GITHUB_API_URL", "https://models.inference.ai.azure.com")
        self.timeout = int(os.getenv("GITHUB_MODEL_TIMEOUT", "30"))
        
        # Create tenacity-based retry configuration
        self.retry_config = create_ai_retry_config("GITHUB")
        self.http_client = HTTPRetryClient(self.retry_config, self.timeout)
        
        # Mask token for logging
        masked_token = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "***"
        logger.info(f"GitHub provider initialized - Model: {self.model}, API URL: {self.api_url}, Token: {masked_token}, Timeout: {self.timeout}s")
        logger.info(f"Retry config - Max retries: {self.retry_config.max_retries}, RPM limit: {self.retry_config.rate_limiter.requests_per_minute if self.retry_config.rate_limiter else 'None'}")
    
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation using GitHub Models with tenacity retry logic."""
        max_tokens = kwargs.get("max_tokens", 2000)
        temperature = kwargs.get("temperature", 0.1)
        
        # Log function call
        log_function_call("GitHubProvider.complete_chat", {
            "model": self.model,
            "messages_count": len(messages),
            "max_tokens": max_tokens,
            "temperature": temperature
        })
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            # Use the tenacity-based HTTP retry client
            result = await self.http_client.post_json(
                url=f"{self.api_url}/chat/completions",
                headers=headers,
                json_data=payload,
                operation_name="GitHub Models API"
            )
            
            result_content = result["choices"][0]["message"]["content"]
            
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"GitHub API response preview: {result_content[:200]}{'...' if len(result_content) > 200 else ''}")
            
            return result_content
            
        except Exception as e:
            logger.error(f"GitHub API error: {e}")
            raise
    
    async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured recipe data from HTML using GitHub Models."""
        return await OpenAIProvider.extract_recipe_data(self, html_content, url)
    
    async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """Normalize ingredient texts into structured data."""
        return await OpenAIProvider.normalize_ingredients(self, ingredients)
    
    async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match and rank products for an ingredient using AI."""
        return await OpenAIProvider.match_products(self, ingredient, products)