"""Base AI provider abstract class and common utilities."""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..config.logging_config import get_logger

# Get module logger
logger = get_logger(__name__)

class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation."""
    
    @abstractmethod
    async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured recipe data from HTML using AI."""
    
    @abstractmethod
    async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """Normalize ingredient texts into structured data."""
    
    @abstractmethod
    async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match and rank products for an ingredient."""