"""OpenAI GPT provider implementation."""

import json
import logging
import os
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..config.logging_config import get_logger
from ..utils.ai_helpers import (
    INGREDIENT_NORMALIZATION_PROMPT,
    INGREDIENT_NORMALIZATION_SYSTEM,
    PRODUCT_MATCHING_PROMPT,
    PRODUCT_MATCHING_SYSTEM,
    RECIPE_EXTRACTION_PROMPT,
    RECIPE_EXTRACTION_SYSTEM,
    format_ai_prompt,
    safe_json_parse,
    validate_ingredient_data,
    validate_recipe_data,
)
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
    
    async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured recipe data from HTML using OpenAI."""   

        # Truncate HTML if too long
        if len(html_content) > 8000:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            html_content = str(soup)[:8000]

        # Set system message
        system = RECIPE_EXTRACTION_SYSTEM

        # Use centralized prompt template
        prompt = format_ai_prompt(RECIPE_EXTRACTION_PROMPT, html_content=html_content)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[OpenAI] System message: {system}")
            logger.debug(f"[OpenAI] User message: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.complete_chat(messages, max_tokens=1500)
            # Use centralized JSON parsing with validation
            recipe_data = safe_json_parse(response, fallback={})
            return validate_recipe_data(recipe_data)
        except Exception as e:
            logger.error(f"[OpenAI] Error in extract_recipe_data: {e}")
            # Only log response if it was defined
            try:
                logger.debug(f"[OpenAI] Raw response that failed to parse: {response[:500]}...")
            except NameError:
                logger.debug("[OpenAI] No response received due to earlier error")
            
            # Return minimal structure if parsing fails
            return {
                "title": "Recipe from " + url,
                "description": "",
                "servings": None,
                "prep_time": None,
                "cook_time": None,
                "ingredients": [],
                "instructions": [],
                "image_url": None
            }
    
    async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """Normalize ingredient texts into structured data."""
            
        # Set system message  
        system = INGREDIENT_NORMALIZATION_SYSTEM
        
        # Use centralized prompt template
        prompt = format_ai_prompt(
            INGREDIENT_NORMALIZATION_PROMPT, 
            ingredients_json=json.dumps(ingredients, indent=2)
        )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[OpenAI] System message: {system}")
            logger.debug(f"[OpenAI] User message: {prompt}")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.complete_chat(messages, max_tokens=1000)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[OpenAI] Response: {response}")

            # Use centralized JSON parsing with validation
            ingredient_data = safe_json_parse(response, fallback=[])
            return validate_ingredient_data(ingredient_data)
        except Exception as e:
            logger.error(f"[OpenAI] Error normalizing ingredients: {e}")
            # Only log response if it was defined
            try:
                logger.debug(f"[OpenAI] Raw response that failed to parse: {response[:500]}...")
            except NameError:
                logger.debug("[OpenAI] No response received due to earlier error")
            # Fallback: return basic structure
            return [
                {
                    "name": ing,
                    "quantity": None,
                    "unit": None,
                    "original_text": ing
                }
                for ing in ingredients
            ]
    
    async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match and rank products for an ingredient using AI."""
        if not products:
            return []
        
        # Set system message
        system = PRODUCT_MATCHING_SYSTEM
        
        # Use centralized prompt template
        prompt = format_ai_prompt(
            PRODUCT_MATCHING_PROMPT,
            ingredient=ingredient,
            products_json=json.dumps(products, indent=2)
        )

        logger.debug(f"[OpenAI] System message: {system}")
        logger.debug(f"[OpenAI] User message: {prompt}")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.complete_chat(messages, max_tokens=1500)
            # Use centralized JSON parsing
            ranked_products = safe_json_parse(response, fallback=products)
            return ranked_products if isinstance(ranked_products, list) else products
        except Exception as e:
            logger.error(f"[OpenAI] Error ranking products: {e}")
            # Only log response if it was defined
            try:
                logger.debug(f"[OpenAI] Raw response that failed to parse: {response[:500]}...")
            except NameError:
                logger.debug("[OpenAI] No response received due to earlier error")
            # Fallback: return original products with default scores
            for i, product in enumerate(products):
                product["match_score"] = 100 - (i * 10)  # Simple scoring
            return products