"""AI service for intelligent web crawling and grocery search optimization."""

import os
import json
import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum
import httpx
from bs4 import BeautifulSoup

# Import centralized logging configuration
from ..utils.logging_config import get_logger, log_function_call, log_api_request
from ..utils.ai_helpers import (
    clean_json_response, 
    safe_json_parse,
    validate_ingredient_data,
    validate_recipe_data,
    format_ai_prompt,
    RECIPE_EXTRACTION_PROMPT,
    INGREDIENT_NORMALIZATION_PROMPT,
    PRODUCT_MATCHING_PROMPT,
    ALTERNATIVES_PROMPT
)

# Get module logger
logger = get_logger(__name__)

# AI Provider imports
try:
    import openai
except ImportError:
    openai = None

try:
    import openai as azure_openai  # Use openai library for Azure OpenAI too
    ChatCompletionsClient = True  # Flag to indicate Azure OpenAI availability
except ImportError:
    ChatCompletionsClient = None

try:
    import ollama
except ImportError:
    ollama = None

from ..models import Recipe, Ingredient, Product, StoreSearchResult


class AIProvider(str, Enum):
    """Available AI providers."""
    OPENAI = "openai"
    AZURE = "azure"
    OLLAMA = "ollama"
    GITHUB = "github"


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation."""
        pass
    
    @abstractmethod
    async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured recipe data from HTML using AI."""
        pass
    
    @abstractmethod
    async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """Normalize ingredient texts into structured data."""
        pass
    
    @abstractmethod
    async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match and rank products for an ingredient."""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider."""
    
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
        
        logger.info(f"OpenAI provider initialized - Model: {self.model}, Max tokens: {self.max_tokens}, Temperature: {self.temperature}")
    
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation using OpenAI."""
        start_time = time.time()
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        temperature = kwargs.get("temperature", self.temperature)
        
        logger.debug(f"OpenAI API call - Model: {self.model}, Messages: {len(messages)}, Max tokens: {max_tokens}, Temperature: {temperature}")
        
        # Log messages in debug mode (truncate for readability)
        if logger.isEnabledFor(logging.DEBUG):
            for i, msg in enumerate(messages):
                content = msg.get('content', '')[:200] + '...' if len(msg.get('content', '')) > 200 else msg.get('content', '')
                logger.debug(f"  Message {i+1} ({msg.get('role', 'unknown')}): {content}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            duration = time.time() - start_time
            result_content = response.choices[0].message.content
            
            logger.info(f"OpenAI API success - Duration: {duration:.2f}s, Response length: {len(result_content)} chars")
            logger.debug(f"OpenAI response preview: {result_content[:300]}{'...' if len(result_content) > 300 else ''}")
            
            return result_content
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"OpenAI API error after {duration:.2f}s: {e}")
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
        
        system = """You are a web crawler / price comparison assistant that does the following steps:
        Reads recipes online — extracts the list of ingredients and quantities and return only valid JSON.
        """

        # Use centralized prompt template
        prompt = format_ai_prompt(RECIPE_EXTRACTION_PROMPT, html_content=html_content)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[OpenAI] [extract_recipe_data] System message: {system}")
            logger.debug(f"[OpenAI] [extract_recipe_data] User message: {prompt}")

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
            logger.debug(f"[OpenAI] Raw response that failed to parse: {response[:500]}...")
            
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
        system = "You are an expert at parsing cooking ingredients. Return only valid JSON."
        
        # Use centralized prompt template
        prompt = format_ai_prompt(
            INGREDIENT_NORMALIZATION_PROMPT, 
            ingredients_json=json.dumps(ingredients, indent=2)
        )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[OpenAI] [normalize_ingredients] System message: {system}")
            logger.debug(f"[OpenAI] [normalize_ingredients] User message: {prompt}")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.complete_chat(messages, max_tokens=1000)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[OpenAI] [normalize_ingredients] Response: {response}")

            # Use centralized JSON parsing with validation
            ingredient_data = safe_json_parse(response, fallback=[])
            return validate_ingredient_data(ingredient_data)
        except Exception as e:
            logger.error(f"[OpenAI] Error normalizing ingredients: {e}")
            logger.debug(f"[OpenAI] Raw response that failed to parse: {response[:500]}...")
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
        
        system = "You are a grocery shopping expert. Rank products by relevance and quality."
        
        # Use centralized prompt template
        prompt = format_ai_prompt(
            PRODUCT_MATCHING_PROMPT,
            ingredient=ingredient,
            products_json=json.dumps(products, indent=2)
        )

        logger.debug(f"[OpenAI] [match_products] System message: {system}")
        logger.debug(f"[OpenAI] [match_products] User message: {prompt}")

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
            logger.debug(f"[OpenAI] Raw response that failed to parse: {response[:500]}...")
            # Fallback: return original products with default scores
            for i, product in enumerate(products):
                product["match_score"] = 100 - (i * 10)  # Simple scoring
            return products
    

class AzureProvider(BaseAIProvider):
    """Azure OpenAI provider."""
    
    def __init__(self):
        if not openai:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables must be set")
        
        self.client = openai.AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation using Azure OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.1)
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[Azure] Error: {e}")
            raise
    
    async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured recipe data from HTML using Azure OpenAI."""
        # Similar implementation to OpenAI but using Azure client
        return await OpenAIProvider.extract_recipe_data(self, html_content, url)
    
    async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """Normalize ingredient texts into structured data."""
        return await OpenAIProvider.normalize_ingredients(self, ingredients)
    
    async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match and rank products for an ingredient using AI."""
        return await OpenAIProvider.match_products(self, ingredient, products)


class OllamaProvider(BaseAIProvider):
    """Ollama local LLM provider."""
    
    def __init__(self):
        if not ollama:
            raise ImportError("Ollama library not installed. Run: pip install ollama")
        
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        
        # Test connection
        try:
            client = ollama.Client(host=self.base_url)
            client.list()
        except Exception as e:
            raise ConnectionError(f"Cannot connect to Ollama at {self.base_url}: {e}")
    
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation using Ollama."""
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
            print(f"[Ollama] Error: {e}")
            raise
    
    async def extract_recipe_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured recipe data from HTML using Ollama."""
        return await OpenAIProvider.extract_recipe_data(self, html_content, url)
    
    async def normalize_ingredients(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """Normalize ingredient texts into structured data."""
        return await OpenAIProvider.normalize_ingredients(self, ingredients)
    
    async def match_products(self, ingredient: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match and rank products for an ingredient using AI."""
        return await OpenAIProvider.match_products(self, ingredient, products)


class GitHubProvider(BaseAIProvider):
    """GitHub Models provider."""
    
    def __init__(self):
        logger.debug("Initializing GitHub Models provider...")
        
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
        
        self.token = token
        self.model = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
        self.api_url = os.getenv("GITHUB_API_URL", "https://models.inference.ai.azure.com")
        self.timeout = int(os.getenv("GITHUB_MODEL_TIMEOUT", "30"))
        
        # Mask token for logging
        masked_token = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "***"
        logger.info(f"GitHub provider initialized - Model: {self.model}, API URL: {self.api_url}, Token: {masked_token}, Timeout: {self.timeout}s")
    
    async def complete_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Complete a chat conversation using GitHub Models."""
        start_time = time.time()
        max_tokens = kwargs.get("max_tokens", 2000)
        temperature = kwargs.get("temperature", 0.1)
        
        # Log function call
        log_function_call("GitHubProvider.complete_chat", {
            "model": self.model,
            "messages_count": len(messages),
            "max_tokens": max_tokens,
            "temperature": temperature
        })
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
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
                
                payload_size = len(json.dumps(payload).encode('utf-8'))
                logger.debug(f"GitHub API request payload size: {payload_size} bytes")
                
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                duration = time.time() - start_time
                
                # Log API request details
                log_api_request("GitHub", f"{self.api_url}/chat/completions", payload_size, duration, True)
                
                result_content = result["choices"][0]["message"]["content"]

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"GitHub API response preview: {result_content[:200]}{'...' if len(result_content) > 200 else ''}")
                    # logger.debug(f"GitHub API response preview: {result_content}")
                
                return result_content
        except Exception as e:
            duration = time.time() - start_time
            log_api_request("GitHub", f"{self.api_url}/chat/completions", 0, duration, False)
            logger.error(f"GitHub API error after {duration:.2f}s: {e}")
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


class AIService:
    """Main AI service that manages different providers."""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider_name = provider or os.getenv("AI_PROVIDER", "openai")
        self.provider = self._create_provider(self.provider_name)
    
    def _create_provider(self, provider_name: str) -> BaseAIProvider:
        """Create AI provider based on configuration."""
        provider_map = {
            AIProvider.OPENAI: OpenAIProvider,
            AIProvider.AZURE: AzureProvider,
            AIProvider.OLLAMA: OllamaProvider,
            AIProvider.GITHUB: GitHubProvider,
        }
        
        if provider_name not in provider_map:
            raise ValueError(f"Unknown AI provider: {provider_name}")
        
        try:
            return provider_map[provider_name]()
        except Exception as e:
            print(f"[AIService] Error initializing {provider_name} provider: {e}")
            raise
    
    async def extract_recipe_intelligently(self, html_content: str, url: str) -> Recipe:
        """Extract recipe data using AI intelligence."""
        print(f"[AIService] Extracting recipe using {self.provider_name} provider")
        
        try:
            recipe_data = await self.provider.extract_recipe_data(html_content, url)
            
            # Normalize ingredients using AI
            if recipe_data.get("ingredients"):
                normalized_ingredients = await self.provider.normalize_ingredients(
                    recipe_data["ingredients"]
                )
                
                # Convert to Ingredient objects
                ingredients = []
                for ing_data in normalized_ingredients:
                    ingredients.append(Ingredient(
                        name=ing_data.get("name", ""),
                        quantity=ing_data.get("quantity"),
                        unit=ing_data.get("unit"),
                        original_text=ing_data.get("original_text", "")
                    ))
            else:
                ingredients = []
            
            return Recipe(
                title=recipe_data.get("title", "Unknown Recipe"),
                url=url,
                description=recipe_data.get("description", ""),
                servings=recipe_data.get("servings"),
                prep_time=recipe_data.get("prep_time"),
                cook_time=recipe_data.get("cook_time"),
                ingredients=ingredients,
                instructions=recipe_data.get("instructions", []),
                image_url=recipe_data.get("image_url")
            )
        except Exception as e:
            print(f"[AIService] Error extracting recipe: {e}")
            # Fallback to basic parsing
            return Recipe(
                title="Recipe from " + url,
                url=url,
                ingredients=[]
            )
    
    async def optimize_product_matching(self, ingredient: Ingredient, 
                                      store_results: Dict[str, List[Product]]) -> Dict[str, List[Product]]:
        """Use AI to optimize product matching and ranking."""
        print(f"[AIService] Optimizing product matching for '{ingredient.name}'")
        
        optimized_results = {}
        
        for store_name, products in store_results.items():
            if not products:
                optimized_results[store_name] = []
                continue
            
            try:
                # Convert products to dict format for AI processing
                products_data = []
                for product in products:
                    products_data.append({
                        "title": product.title,
                        "price": product.price,
                        "brand": product.brand,
                        "size": product.size,
                        "store": product.store
                    })
                
                # Use AI to rank products
                ranked_products = await self.provider.match_products(
                    ingredient.name, products_data
                )
                
                # Convert back to Product objects and update with scores
                optimized_products = []
                for i, ranked_data in enumerate(ranked_products):
                    # Find original product
                    original_product = next(
                        (p for p in products if p.title == ranked_data.get("title")),
                        None
                    )
                    if original_product:
                        # Create new product with AI score
                        optimized_products.append(Product(
                            title=original_product.title,
                            price=original_product.price,
                            store=original_product.store,
                            url=original_product.url,
                            image_url=original_product.image_url,
                            brand=original_product.brand,
                            size=original_product.size,
                            unit_price=original_product.unit_price,
                            availability=original_product.availability
                        ))
                
                optimized_results[store_name] = optimized_products
                
            except Exception as e:
                print(f"[AIService] Error optimizing products for {store_name}: {e}")
                optimized_results[store_name] = products
        
        return optimized_results
    
    async def suggest_alternatives(self, ingredient: Ingredient) -> List[str]:
        """Suggest alternative ingredients using AI."""
        system = "You are a culinary expert. Suggest ingredient alternatives."
        
        # Use centralized prompt template
        prompt = format_ai_prompt(ALTERNATIVES_PROMPT, ingredient=ingredient.name)

        logger.debug(f"[AIService] [suggest_alternatives] System message: {system}")
        logger.debug(f"[AIService] [suggest_alternatives] User message: {prompt}")

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.provider.complete_chat(messages, max_tokens=200)
            
            # Use centralized JSON parsing
            alternatives = safe_json_parse(response, fallback=[])
            return alternatives if isinstance(alternatives, list) else []
        except Exception as e:
            logger.error(f"[AIService] Error suggesting alternatives: {e}")
            logger.debug(f"[AIService] Raw response that failed to parse: {response[:200]}...")
            return []


# Global AI service instance
ai_service = None

def get_ai_service() -> AIService:
    """Get or create the global AI service instance."""
    global ai_service
    if ai_service is None:
        ai_service = AIService()
    return ai_service