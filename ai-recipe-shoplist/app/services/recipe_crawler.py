"""Simple recipe crawler service."""

import httpx
from bs4 import BeautifulSoup

from ..models import Ingredient, Recipe


class SimpleCrawler:
    """Simple recipe crawler for basic functionality."""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    async def fetch_recipe(self, url: str) -> Recipe:
        """Fetch and parse a recipe from URL."""
        print(f"[SimpleCrawler] Fetching recipe from: {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            html_content = response.text
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Simple extraction
        title = "Sample Recipe"
        title_elem = soup.find('h1')
        if title_elem:
            title = title_elem.get_text().strip()
        
        # Mock ingredients for demo
        ingredients = [
            Ingredient(name="chicken breast", quantity=2, original_text="2 chicken breasts"),
            Ingredient(name="vegetables", quantity=1, unit="cup", original_text="1 cup mixed vegetables"),
            Ingredient(name="rice", quantity=1, unit="cup", original_text="1 cup rice"),
        ]
        
        return Recipe(
            title=title,
            url=url,
            ingredients=ingredients,
            instructions=["Cook ingredients", "Serve hot"]
        )


# Global instance
recipe_crawler = SimpleCrawler()