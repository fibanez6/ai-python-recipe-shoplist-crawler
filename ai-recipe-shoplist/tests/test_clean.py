import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Add the app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config.logging_config import get_logger, setup_logging
from app.services.content_storage import ContentStorage  # Import ContentStorage
from app.utils.html_helpers import clean_html_for_ai
from app.utils.ai_helpers import (
    INGREDIENT_NORMALIZATION_PROMPT,
    clean_json_response,
    format_ai_prompt,
    safe_json_parse,
    validate_ingredient_data,
    validate_recipe_data,
)
from app.models import Ingredient, QuantityUnit  # Import Ingredient

url = "https://www.allrecipes.com/recipe/222331/chef-johns-gazpacho/"

content_storage = ContentStorage(tmp_folder=Path("tmp/web_cache"), enable_saving=False, enable_loading=True)

def save(name: str, content: str):
    content_folder = Path("tmp/test")
    content_folder.mkdir(parents=True, exist_ok=True)

    file = content_folder / f"{name}.html"
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

    
def test_clean():
    disk_content = content_storage.load_content(url)
    original_content = disk_content.get('original_content', '')

    logger = get_logger(__name__)

    logger.info("Loading content from disk for cleaning test")
    save("original", str(original_content))

    logger.info("Cleaning HTML content for AI")
    cleaned_content = clean_html_for_ai(original_content)
    save("cleaned", cleaned_content)

    pass


def test_model():

    complex_response = '''
[
  {
    "name": "ripe tomatoes",
    "quantity": 2,
    "unit": "pounds",
    "original_text": "2 pounds ripe tomatoes, chopped"
  },
  {
    "name": "cucumber",
    "quantity": 1,
    "unit": null,
    "original_text": "1 cucumber, peeled and chopped"
  },
  {
    "name": "bell pepper",
    "quantity": 1,
    "unit": null,
    "original_text": "1 bell pepper, chopped"
  },
  {
    "name": "small red onion",
    "quantity": 1,
    "unit": null,
    "original_text": "1 small red onion, chopped"
  },
  {
    "name": "garlic",
    "quantity": 2,
    "unit": "cloves",
    "original_text": "2 cloves garlic, minced"
  },
  {
    "name": "tomato juice",
    "quantity": 3,
    "unit": "cups",
    "original_text": "3 cups tomato juice"
  },
  {
    "name": "olive oil",
    "quantity": 0.25,
    "unit": "cup",
    "original_text": "1/4 cup olive oil"
  },
  {
    "name": "red wine vinegar",
    "quantity": 2,
    "unit": "tablespoons",
    "original_text": "2 tablespoons red wine vinegar"
  },
  {
    "name": "salt",
    "quantity": 1,
    "unit": "teaspoon",
    "original_text": "1 teaspoon salt"
  },
  {
    "name": "ground black pepper",
    "quantity": 0.25,
    "unit": "teaspoon",
    "original_text": "1/4 teaspoon ground black pepper"
  },
  {
    "name": "cayenne pepper",
    "quantity": 0.25,
    "unit": "teaspoon",
    "original_text": "1/4 teaspoon cayenne pepper"
  },
  {
    "name": "chopped fresh basil",
    "quantity": 0.25,
    "unit": "cup",
    "original_text": "1/4 cup chopped fresh basil"
  }
]
    '''

    parsed = safe_json_parse(complex_response)
    validated = validate_ingredient_data(parsed)

    for item in validated:
        print()
        print()
        print(f"Validated ingredient: {item}")

        ingredient = Ingredient(**item)
        print(f"Created Ingredient model: {ingredient}")
    pass


def main():
    """Run all AI utility tests."""
    setup_logging(debug=True)
    logger = get_logger(__name__)
    
    logger.info("AI Utilities Test Suite")
    
    try:
        # test_clean()
        test_model()
        
        logger.info("✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main()