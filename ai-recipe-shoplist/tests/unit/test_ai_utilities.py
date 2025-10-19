#!/usr/bin/env python3
"""
Test script for the centralized AI utility functions.
Demonstrates JSON cleaning, validation, and prompt formatting.
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.logging_config import get_logger, setup_logging
from app.utils.ai_helpers import (
    INGREDIENT_NORMALIZATION_PROMPT,
    clean_json_response,
    format_ai_prompt,
    safe_json_parse,
    validate_ingredient_data,
    validate_recipe_data,
)


def test_json_cleaning():
    """Test JSON response cleaning functions."""
    logger = get_logger(__name__)
    
    logger.info("Testing JSON Cleaning Functions")
    logger.info("=" * 40)
    
    test_cases = [
        # Basic markdown cleaning
        '```json\n{"key": "value"}\n```',
        
        # Response with extra text
        'Here is the data:\n```json\n[{"name": "tomato"}]\n```\nThat\'s all!',
        
        # JSON without markdown
        '{"clean": "json"}',
        
        # Malformed response
        'Some text {"embedded": "json"} more text',
        
        # Array response
        '```\n["item1", "item2", "item3"]\n```'
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\nTest case {i}:")
        logger.info(f"  Input: {test_case[:50]}{'...' if len(test_case) > 50 else ''}")
        
        cleaned = clean_json_response(test_case)
        logger.info(f"  Cleaned: {cleaned}")
        
        parsed = safe_json_parse(test_case)
        logger.info(f"  Parsed: {parsed}")
        
        print()

def test_ingredient_validation():
    """Test ingredient data validation."""
    logger = get_logger(__name__)
    
    logger.info("Testing Ingredient Validation")
    logger.info("=" * 40)
    
    test_data = [
        {"name": "tomato", "quantity": 2, "unit": "piece", "original_text": "2 tomatoes"},
        {"name": "", "quantity": 1, "unit": "cup"},  # Invalid: empty name
        {"name": "flour", "quantity": "invalid", "unit": "cup", "original_text": "1 cup flour"},
        {"name": "salt", "original_text": "salt to taste"},  # Missing quantity/unit
        "invalid_item",  # Not a dict
    ]
    
    logger.info(f"Input data: {test_data}")
    
    validated = validate_ingredient_data(test_data)
    logger.info(f"Validated data: {validated}")
    
    print()

def test_recipe_validation():
    """Test recipe data validation."""
    logger = get_logger(__name__)
    
    logger.info("Testing Recipe Validation")
    logger.info("=" * 40)
    
    test_recipe = {
        "title": "Test Recipe",
        "servings": "4",  # String that should be converted to int
        "ingredients": "not a list",  # Invalid type
        "instructions": ["Step 1", "Step 2"],
        "invalid_field": "should be ignored"
    }
    
    logger.info(f"Input recipe: {test_recipe}")
    
    validated = validate_recipe_data(test_recipe)
    logger.info(f"Validated recipe: {validated}")
    
    print()

def test_prompt_formatting():
    """Test prompt template formatting."""
    logger = get_logger(__name__)
    
    logger.info("Testing Prompt Formatting")
    logger.info("=" * 40)
    
    # Test ingredient normalization prompt
    ingredients = ["2 tomatoes", "1 cup flour", "salt to taste"]
    formatted_prompt = format_ai_prompt(
        INGREDIENT_NORMALIZATION_PROMPT,
        ingredients_json=str(ingredients)
    )
    
    logger.info("Formatted ingredient prompt:")
    logger.info(formatted_prompt[:200] + "...")
    
    print()

def test_complex_response():
    """Test with a complex AI response that includes markdown and extra text."""
    logger = get_logger(__name__)
    
    logger.info("Testing Complex AI Response")
    logger.info("=" * 40)
    
    complex_response = '''
Here are the normalized ingredients:

```json
[
  {
    "name": "Tomatoes",
    "quantity": null,
    "unit": null,
    "original_text": "Tomatoes - juicy ripe ones are key to great flavour."
  },
  {
    "name": "Cucumber", 
    "quantity": 1,
    "unit": null,
    "original_text": "Cucumber - one cucumber around 20cm/8″ long, peeled for smoother soup."
  }
]
```

Hope this helps!
    '''
    
    logger.info("Complex response input:")
    logger.info(complex_response[:100] + "...")
    
    # Test different parsing methods
    cleaned = clean_json_response(complex_response)
    logger.info(f"\nCleaned response: {cleaned[:100]}...")
    
    parsed = safe_json_parse(complex_response)
    logger.info(f"\nSafe parsed result: {parsed}")
    
    if parsed:
        validated = validate_ingredient_data(parsed)
        logger.info(f"\nValidated ingredients: {validated}")
    
    print()

def main():
    """Run all AI utility tests."""
    setup_logging(debug=True)
    logger = get_logger(__name__)
    
    logger.info("AI Utilities Test Suite")
    logger.info("=" * 60)
    
    try:
        test_json_cleaning()
        test_ingredient_validation() 
        test_recipe_validation()
        test_prompt_formatting()
        test_complex_response()
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main()