"""Simple store crawler with mock data."""

import asyncio
import random
from typing import List, Dict
from ..models import Product, StoreSearchResult, Ingredient


class SimpleStoreCrawler:
    """Simple store crawler with mock grocery data."""
    
    def __init__(self):
        self.stores = ["coles", "woolworths", "aldi", "iga"]
    
    async def search_all_stores(self, ingredients: List[Ingredient], 
                               store_names: List[str] = None) -> Dict[str, List[StoreSearchResult]]:
        """Search all stores for ingredients."""
        if store_names:
            active_stores = [s for s in self.stores if s in store_names]
        else:
            active_stores = self.stores
        
        results = {}
        
        for store in active_stores:
            store_results = []
            
            for ingredient in ingredients:
                # Generate mock products
                products = await self._generate_mock_products(ingredient, store)
                
                store_results.append(StoreSearchResult(
                    ingredient_name=ingredient.name,
                    store_name=store,
                    products=products,
                    search_time=0.1
                ))
            
            results[store] = store_results
        
        return results
    
    async def _generate_mock_products(self, ingredient: Ingredient, store: str) -> List[Product]:
        """Generate mock products for an ingredient."""
        await asyncio.sleep(0.05)  # Simulate network delay
        
        base_price = random.uniform(2.0, 10.0)
        
        # Store-specific pricing
        if store == "aldi":
            base_price *= 0.85  # ALDI typically cheaper
        elif store == "iga":
            base_price *= 1.15  # IGA typically more expensive
        
        products = [
            Product(
                title=f"{ingredient.name.title()} - {store.title()} Brand",
                price=round(base_price, 2),
                store=store,
                url=f"https://{store}.com.au/product/{ingredient.name.replace(' ', '-')}",
                brand=f"{store.title()}",
                size="500g"
            ),
            Product(
                title=f"Premium {ingredient.name.title()}",
                price=round(base_price * 1.3, 2),
                store=store,
                url=f"https://{store}.com.au/product/premium-{ingredient.name.replace(' ', '-')}",
                brand="Premium Brand",
                size="400g"
            )
        ]
        
        return products
    
    def get_available_stores(self) -> List[str]:
        """Get list of available stores."""
        return self.stores


# Global instance
store_crawler = SimpleStoreCrawler()