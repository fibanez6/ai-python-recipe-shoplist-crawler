import asyncio
import os
import sys

import rich
from dotenv import load_dotenv

from app.config.logging_config import setup_logging
from app.services.web_fetcher import get_web_fetcher

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

url="https://www.coles.com.au/_next/data/20251029.1-5acc651e3b5f8a27a9fa067cf11fc08619865a7b/en/search/products.json?q=tomato"


load_dotenv()

logger = setup_logging()

async def fetch_page():
    web_fetcher = get_web_fetcher()
    fetch_result = await web_fetcher.fetch_html(url, clean_html=True)


if __name__ == "__main__":
    asyncio.run(fetch_page())