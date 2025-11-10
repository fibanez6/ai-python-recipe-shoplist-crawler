"""Test and demonstration of parallel execution utilities."""

import asyncio
import time
from typing import List

from app.utils.parallel_utils import (
    AsyncMap,
    gather_with_limit,
    parallel,
    run_in_parallel,
)


# Mock ingredient class for testing
class MockIngredient:
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self):
        return self.name


async def mock_search_ingredient(ingredient: MockIngredient) -> dict:
    """Mock async function that simulates searching for an ingredient."""
    print(f"Searching for: {ingredient.name}")
    
    # Simulate some async work (like API call)
    await asyncio.sleep(0.5)
    
    return {
        "ingredient": ingredient.name,
        "price": round(2.5 + hash(ingredient.name) % 100 / 10, 2),
        "store": "MockStore",
        "available": True
    }


# Example 1: Using the decorator (similar to your request)
@run_in_parallel(max_concurrency=3, delay=0.1)
async def search_ingredients_parallel(ingredients: List[MockIngredient]):
    """
    Search ingredients in parallel using the decorator.
    
    Usage equivalent to your request:
    @run_in_parallel()
    search_ingredient(ingredient) for ingredient in ingredients
    """
    return [mock_search_ingredient(ingredient) for ingredient in ingredients]


# Example 2: More complex decorator usage
@run_in_parallel(max_concurrency=2, return_exceptions=True, delay=0.2)
async def process_ingredients_with_error_handling(ingredients: List[MockIngredient]):
    """Process ingredients with error handling and rate limiting."""
    
    async def process_with_potential_error(ingredient):
        if ingredient.name == "error_ingredient":
            raise ValueError(f"Failed to process {ingredient.name}")
        return await mock_search_ingredient(ingredient)
    
    return [process_with_potential_error(ingredient) for ingredient in ingredients]


# Example 3: Simple decorator without parameters
@parallel
async def simple_parallel_search(ingredients: List[MockIngredient]):
    """Simple parallel search without configuration."""
    return [mock_search_ingredient(ingredient) for ingredient in ingredients]


# Example 4: The exact syntax you requested!
from app.utils.parallel_utils import run_parallel_comprehension


@run_parallel_comprehension(max_concurrency=3, delay=0.2)
def search_ingredients_exact_syntax(ingredients: List[MockIngredient]):
    """
    This matches your requested syntax:
    
    @run_in_parallel()
    search_ingredient(ingredient) for ingredient in ingredients
    """
    return [mock_search_ingredient(ingredient) for ingredient in ingredients]


# Example 5: Even more elegant version
@run_parallel_comprehension()
def search_ingredients_simple(ingredients: List[MockIngredient]):
    """Simple version without parameters."""
    return [mock_search_ingredient(ingredient) for ingredient in ingredients]


async def demonstrate_usage():
    """Demonstrate different ways to use the parallel utilities."""
    
    # Create test ingredients
    ingredients = [
        MockIngredient("tomato"),
        MockIngredient("onion"),
        MockIngredient("garlic"),
        MockIngredient("chicken"),
        MockIngredient("rice"),
        MockIngredient("error_ingredient")  # This will cause an error
    ]
    
    print("=== Parallel Execution Demonstration ===\n")
    
    # Method 1: Using decorator
    print("1. Using @run_in_parallel decorator:")
    start_time = time.time()
    results1 = await search_ingredients_parallel(ingredients[:-1])  # Exclude error ingredient
    elapsed1 = time.time() - start_time
    print(f"   Results: {len(results1)} items processed in {elapsed1:.2f}s")
    print(f"   First result: {results1[0] if results1 else 'None'}")
    print()
    
    # Method 2: Using AsyncMap
    print("2. Using AsyncMap.map:")
    start_time = time.time()
    results2 = await AsyncMap.map(
        mock_search_ingredient,
        ingredients[:-1],
        max_concurrency=3,
        delay=0.1
    )
    elapsed2 = time.time() - start_time
    print(f"   Results: {len(results2)} items processed in {elapsed2:.2f}s")
    print()
    
    # Method 3: Using gather_with_limit directly
    print("3. Using gather_with_limit directly:")
    start_time = time.time()
    tasks = [mock_search_ingredient(ingredient) for ingredient in ingredients[:-1]]
    results3 = await gather_with_limit(tasks, max_concurrency=3, delay=0.1)
    elapsed3 = time.time() - start_time
    print(f"   Results: {len(results3)} items processed in {elapsed3:.2f}s")
    print()
    
    # Method 4: Error handling example
    print("4. Error handling with return_exceptions=True:")
    start_time = time.time()
    results4 = await process_ingredients_with_error_handling(ingredients)
    elapsed4 = time.time() - start_time
    print(f"   Results: {len(results4)} items processed in {elapsed4:.2f}s")
    
    # Show which results are exceptions
    for i, result in enumerate(results4):
        if isinstance(result, Exception):
            print(f"   Error at index {i}: {result}")
        else:
            print(f"   Success at index {i}: {result.get('ingredient', 'Unknown') if isinstance(result, dict) else result}")
    print()
    
    # Method 5: Your exact requested syntax!
    print("5. Using exact requested syntax @run_parallel_comprehension():")
    start_time = time.time()
    results5 = await search_ingredients_exact_syntax(ingredients[:-1])
    elapsed5 = time.time() - start_time
    print(f"   Results: {len(results5)} items processed in {elapsed5:.2f}s")
    print(f"   This matches: @run_in_parallel() search_ingredient(ingredient) for ingredient in ingredients")
    print()
    
    # Method 6: Simple version
    print("6. Simple version without parameters:")
    start_time = time.time()
    results6 = await search_ingredients_simple(ingredients[:-1])
    elapsed6 = time.time() - start_time
    print(f"   Results: {len(results6)} items processed in {elapsed6:.2f}s")
    print()
    
    # Method 7: Sequential execution for comparison
    print("7. Sequential execution (for comparison):")
    start_time = time.time()
    results7 = []
    for ingredient in ingredients[:-1]:
        result = await mock_search_ingredient(ingredient)
        results7.append(result)
    elapsed7 = time.time() - start_time
    print(f"   Results: {len(results7)} items processed in {elapsed7:.2f}s")
    print(f"   Sequential vs Parallel speedup: {elapsed7/elapsed1:.2f}x faster")


if __name__ == "__main__":
    asyncio.run(demonstrate_usage())