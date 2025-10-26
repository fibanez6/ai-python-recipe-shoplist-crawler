"""
AI utility functions for response processing and data handling.
"""

import json
import logging
import re
from typing import Any, Dict, List, Union

# Get module logger
logger = logging.getLogger(__name__)


def clean_json_response(response: str) -> str:
    """
    Clean AI response by removing markdown code block markers and extra text.
    
    Args:
        response: Raw AI response that may contain markdown markers
        
    Returns:
        Cleaned JSON string ready for parsing
        
    Examples:
        >>> clean_json_response('```json\\n{"key": "value"}\\n```')
        '{"key": "value"}'
        
        >>> clean_json_response('Here is the data: {"key": "value"}')
        '{"key": "value"}'
    """
    if not response:
        return response
    
    # Remove markdown code block markers
    if response.startswith('```json'):
        response = response[7:]  # Remove ```json
    elif response.startswith('```'):
        response = response[3:]   # Remove ```
    
    if response.endswith('```'):
        response = response[:-3]  # Remove trailing ```
    
    # Strip whitespace
    response = response.strip()
    
    # If response still doesn't start with { or [, try to find JSON
    if not response.startswith(('{', '[')):
        # Look for JSON starting with { or [
        json_start = -1
        for i, char in enumerate(response):
            if char in ('{', '['):
                json_start = i
                break
        
        if json_start >= 0:
            response = response[json_start:]
    
    return response


def safe_json_parse(response: str, fallback: Any = None) -> Any:
    """
    Safely parse JSON response with automatic cleaning and fallback.
    
    Args:
        response: Raw AI response
        fallback: Value to return if parsing fails
        
    Returns:
        Parsed JSON object or fallback value
    """
    try:
        # Check if response looks like an error message
        if not response or isinstance(response, str) and (
            response.startswith(("Internal", "Error", "HTTP", "500", "429", "503")) or
            "error" in response.lower() or
            "exception" in response.lower() or
            len(response.strip()) < 2
        ):
            logger.warning(f"AI response appears to be an error: {response[:100]}...")
            return fallback
            
        cleaned_response = clean_json_response(response)
        
        # Double-check that we have something that looks like JSON
        if not cleaned_response or not cleaned_response.strip().startswith(('{', '[')):
            logger.warning(f"Response doesn't appear to be JSON: {cleaned_response[:100]}...")
            return fallback
            
        return json.loads(cleaned_response)
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"JSON parsing failed: {e}. Response: {response[:200]}...")
        return fallback


def extract_json_from_text(text: str) -> Union[Dict, List, None]:
    """
    Extract the first valid JSON object or array from text.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        First valid JSON object/array found, or None
    """
    # Try to find JSON objects {...} or arrays [...]
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple object pattern
        r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',  # Simple array pattern
    ]
    
    for pattern in json_patterns:
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            try:
                candidate = match.group(0)
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    
    return None


def normalize_ai_response(response: str, expected_type: str = "auto") -> Any:
    """
    Normalize AI response to expected format.
    
    Args:
        response: Raw AI response
        expected_type: Expected response type ("object", "array", "string", "auto")
        
    Returns:
        Normalized response
    """
    if not response:
        return None
    
    # Try JSON parsing first
    json_result = safe_json_parse(response)
    if json_result is not None:
        return json_result
    
    # If JSON parsing fails, try extraction
    extracted = extract_json_from_text(response)
    if extracted is not None:
        return extracted
    
    # If expected type is string, return cleaned text
    if expected_type == "string":
        return clean_json_response(response)
    
    # Return None if nothing worked
    return None


def validate_ingredient_data(data: List[Dict]) -> List[Dict]:
    """
    Validate and clean ingredient data from AI response.
    
    Args:
        data: List of ingredient dictionaries
        
    Returns:
        Validated and cleaned ingredient list
    """
    if not isinstance(data, list):
        return []
    
    validated = []
    for item in data:
        if not isinstance(item, dict):
            continue
        
        # Ensure required fields exist
        ingredient = {
            "name": str(item.get("name", "")).strip(),
            "quantity": item.get("quantity"),
            "unit": item.get("unit"),
            "original_text": str(item.get("original_text", "")).strip()
        }
        
        # Only add if name is not empty
        if ingredient["name"]:
            validated.append(ingredient)
    
    return validated


def validate_recipe_data(data: Dict) -> Dict:
    """
    Validate and clean recipe data from AI response.
    
    Args:
        data: Recipe dictionary
        
    Returns:
        Validated and cleaned recipe data
    """
    if not isinstance(data, dict):
        return {}
    
    # Set defaults for required fields
    recipe = {
        "title": str(data.get("title", "Unknown Recipe")).strip(),
        "description": str(data.get("description", "")).strip(),
        "servings": data.get("servings"),
        "prep_time": data.get("prep_time"),
        "cook_time": data.get("cook_time"),
        "ingredients": data.get("ingredients", []),
        "instructions": data.get("instructions", []),
        "image_url": data.get("image_url")
    }
    
    # Validate servings as number
    if recipe["servings"] is not None:
        try:
            recipe["servings"] = int(recipe["servings"])
        except (ValueError, TypeError):
            recipe["servings"] = None
    
    # Ensure ingredients and instructions are lists
    if not isinstance(recipe["ingredients"], list):
        recipe["ingredients"] = []
    
    if not isinstance(recipe["instructions"], list):
        recipe["instructions"] = []
    
    return recipe


def format_ai_prompt(template: str, **kwargs) -> str:
    """
    Format AI prompt template with parameters.
    
    Args:
        template: Prompt template with {placeholders}
        **kwargs: Values to substitute in template
        
    Returns:
        Formatted prompt string
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required template parameter: {e}")


# Common prompt templates

RECIPE_EXTRACTION_SYSTEM = """You are a web crawler / price comparison assistant that does the following steps:
Reads recipes online — extracts the list of ingredients and quantities and return only valid JSON.

Required fields:
- title: recipe name
- description: brief description
- servings: number of servings (integer or null)
- prep_time: preparation time (string or null)
- cook_time: cooking time (string or null)
- ingredients: array of ingredient strings
- instructions: array of instruction steps
- image_url: main recipe image URL (or null)
"""

RECIPE_EXTRACTION_PROMPT = """
Extract recipe information from this HTML content and return as JSON:

HTML content:
{html_content}

Return only valid JSON, no additional text.
"""

INGREDIENT_NORMALIZATION_SYSTEM = "You are an expert at parsing cooking ingredients. Return only valid JSON."

INGREDIENT_NORMALIZATION_PROMPT = """
Parse these ingredient texts into structured data. For each ingredient, extract:
- name: clean ingredient name (e.g., "flour", "chicken breast")
- quantity: numeric amount (float or null)
- unit: measurement unit (e.g., "cup", "tbsp", "kg", "g", "lb") or null
- original_text: the original input text

Ingredients:
{ingredients_json}

Return as JSON array with objects for each ingredient.
"""

PRODUCT_MATCHING_SYSTEM = "You are a grocery shopping expert. Rank products by relevance and quality."

PRODUCT_MATCHING_PROMPT = """
Rank these grocery products by how well they match the ingredient "{ingredient}".
Consider:
1. Name similarity and relevance
2. Brand quality
3. Value for money (price vs size)
4. Organic/premium options

Products:
{products_json}

Return the products array sorted by match quality (best first).
Include a "match_score" field (0-100) for each product.
Return only valid JSON.
"""

ALTERNATIVES_PROMPT = """
Suggest 3-5 alternative ingredients for "{ingredient}" that could be used in cooking.
Consider:
- Similar taste profile
- Similar cooking properties
- Availability in grocery stores
- Dietary restrictions (if any)

Return as a JSON array of strings, no additional text.
"""

RECIPE_SHOPPING_ASSISTANT_SYSTEM =  """
Simulate real-world shopping assistant. that does the following steps:
- Reads recipes online — extracts the list of ingredients and quantities
- Creates a unified shopping list — merging duplicate ingredients and standardizing units.
- Searches Coles, Woolworths and Aldi (Australia's three main grocery chains) to:
-- Find each ingredient, with quantity and unit.
-- Maximize savings by finding the best prices for each ingredient.
-- Suggest the best store (or a mixed basket for cheapest total).
"""

RECIPE_SHOPPING_ASSISTANT_PROMPT = """
Given me a recipe URL "{url}", extract ingredients and find current prices from Coles and Woolworths (using real web data).
"""