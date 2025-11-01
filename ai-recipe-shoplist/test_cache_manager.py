import asyncio
import json
import os
import sys
from pathlib import Path

import rich
from dotenv import load_dotenv

from app.config.logging_config import setup_logging
from app.manager.cache_manager import get_cache_manager
from app.services.web_fetcher import get_web_fetcher

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

url="https://www.coles.com.au/_next/data/20251029.1-5acc651e3b5f8a27a9fa067cf11fc08619865a7b/en/search/products.json?q=tomato"


load_dotenv()

logger = setup_logging()


def save_content():
    content_cache = get_cache_manager()

    url="https://www.coles.com.au/search/products?q=tomatoes&limit=12"
    data = """<html><body><h1>Test</h1></body></html>"""

    content = content_cache.save(url, data, format="html")
    rich.print_json(json.dumps(content, indent=2))

def save_content_alias():
    content_cache = get_cache_manager()

    url="https://www.coles.com.au/search/products?q=tomatoes&limit=12"
    data = """{"title": "Test","items": [{"name": "Tomato", "quantity": 5},{"name": "Potato", "quantity": 3}]}"""
    alias = "processed"

    content = content_cache.save(url, data, format="json", alias=alias)
    rich.print_json(json.dumps(content, indent=2))


def load_content():
    content_cache = get_cache_manager()

    url = "https://www.coles.com.au/search/products?q=tomatoes&limit=12"

    content = content_cache.load(url)
    rich.print_json(json.dumps(content, indent=2))

def load_content_alias():
    content_cache = get_cache_manager()

    url = "https://www.coles.com.au/search/products?q=tomatoes&limit=12"
    alias = "processed"

    content = content_cache.load(url, alias=alias)
    rich.print_json(json.dumps(content, indent=2))


if __name__ == "__main__":
    save_content()
    load_content()
    rich.print("----")
    save_content_alias()
    load_content_alias()