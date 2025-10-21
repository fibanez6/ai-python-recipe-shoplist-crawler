"""OpenAI GPT provider implementation."""

import logging
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

# OpenAI imports
try:
    import openai
except ImportError:
    openai = None


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider with tenacity-based retry logic."""
    
    def __init__(self):
        logger.debug("Initializing OpenAI provider...")
        
        if not openai:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.name = "OpenAIProvider"
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
        
        # Create tenacity-based retry configuration (OpenAI has higher rate limits typically)
        self.retry_config = create_ai_retry_config("OPENAI", requests_per_minute=60)
        
        logger.info(f"OpenAI provider initialized - Model: {self.model}, Max tokens: {self.max_tokens}, Temperature: {self.temperature}")
        logger.info(f"Retry config - Max retries: {self.retry_config.max_retries}, RPM limit: {self.retry_config.rate_limiter.requests_per_minute if self.retry_config.rate_limiter else 'None'}")
    
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation using OpenAI with tenacity retry logic."""
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        temperature = kwargs.get("temperature", self.temperature)
        
        logger.debug(f"OpenAI API call - Model: {self.model}, Messages: {len(messages)}, Max tokens: {max_tokens}, Temperature: {temperature}")
        
        # Log messages in debug mode (truncate for readability)
        if logger.isEnabledFor(logging.DEBUG):
            for i, msg in enumerate(messages):
                content = msg.get('content', '')[:200] + '...' if len(msg.get('content', '')) > 200 else msg.get('content', '')
                logger.debug(f"  Message {i+1} ({msg.get('role', 'unknown')}): {content}")
        
        @with_ai_retry(self.retry_config)
        async def make_openai_request():
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                # Convert OpenAI-specific errors to our retry framework
                error_str = str(e).lower()
                if "rate limit" in error_str or "429" in error_str:
                    raise RateLimitError(f"OpenAI rate limit: {e}")
                elif any(keyword in error_str for keyword in ["server", "503", "502", "500"]):
                    raise ServerError(f"OpenAI server error: {e}")
                elif any(keyword in error_str for keyword in ["timeout", "connection"]):
                    raise NetworkError(f"OpenAI network error: {e}")
                else:
                    raise  # Let tenacity decide if it's retryable
        
        try:
            result_content = await make_openai_request()
            logger.debug(f"OpenAI response preview: {result_content[:300]}{'...' if len(result_content) > 300 else ''}")
            return result_content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
   