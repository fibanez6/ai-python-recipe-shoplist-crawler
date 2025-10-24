"""Base AI provider abstract class and common utilities."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..config.pydantic_config import FETCHER_AI_MAX_LENGTH
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

# Get module logger
logger = get_logger(__name__)

class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation."""
    
    # @abstractmethod
    async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured recipe data from HTML using AI."""

        logger.info(f"[{self.name}] Extracting recipe data from URL: {url}")

        # Get max length from environment variable
        max_ai_length = FETCHER_AI_MAX_LENGTH
        
        # Truncate HTML if too long
        if len(html_content) > max_ai_length:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            html_content = str(soup)[:max_ai_length]

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
    
    # @abstractmethod
    async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """Normalize ingredient texts into structured data."""
            
        logger.info(f"[{self.name}] Normalizing ingredients")

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
    
    # @abstractmethod
    async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match and rank products for an ingredient using AI."""

        logger.info(f"[{self.name}] Matching products for ingredient")

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