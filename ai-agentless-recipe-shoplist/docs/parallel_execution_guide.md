# Parallel Execution Utilities

This module provides decorators and utilities for running code in parallel using `asyncio.gather` with additional features like concurrency limits, rate limiting, and error handling.

## Installation

The utilities are located in `app/utils/parallel_utils.py` and can be imported as:

```python
from app.utils.parallel_utils import (
    run_in_parallel,
    run_parallel_comprehension,
    parallel,
    AsyncMap,
    gather_with_limit,
    ParallelComprehension
)
```

## Quick Start - Exact Syntax You Requested

The closest match to your requested syntax is:

```python
from app.utils.parallel_utils import run_parallel_comprehension

@run_parallel_comprehension(max_concurrency=3, delay=0.1)
def search_all_ingredients(ingredients):
    return [search_ingredient(ingredient) for ingredient in ingredients]

# Usage
results = await search_all_ingredients(ingredients)
```

This is equivalent to your request:
```python
@run_in_parallel()
search_ingredient(ingredient) for ingredient in ingredients
```

## Available Methods

### 1. `@run_parallel_comprehension()` - Exact Syntax Match

**Best for**: When you want to parallelize a list comprehension

```python
@run_parallel_comprehension(max_concurrency=5, delay=0.1)
def parallel_search(ingredients):
    return [search_ingredient(ingredient) for ingredient in ingredients]

# Usage
results = await parallel_search(ingredients)
```

**Parameters**:
- `max_concurrency`: Maximum concurrent tasks (default: unlimited)
- `return_exceptions`: Return exceptions as results instead of raising (default: True)
- `delay`: Delay between starting tasks in seconds (default: 0.0)

### 2. `AsyncMap.map()` - Functional Style

**Best for**: When you want explicit control and functional programming style

```python
results = await AsyncMap.map(
    search_ingredient,           # Function to apply
    ingredients,                 # Iterable to process
    max_concurrency=5,
    delay=0.1,
    return_exceptions=True
)
```

### 3. `gather_with_limit()` - Direct Control

**Best for**: When you already have a list of coroutines

```python
tasks = [search_ingredient(ingredient) for ingredient in ingredients]
results = await gather_with_limit(
    tasks,
    max_concurrency=5,
    delay=0.1
)
```

### 4. `@run_in_parallel()` - Decorator Style

**Best for**: When your function returns generators or iterables of coroutines

```python
@run_in_parallel(max_concurrency=5, delay=0.1)
async def search_ingredients(ingredients):
    return [search_ingredient(ingredient) for ingredient in ingredients]

results = await search_ingredients(ingredients)
```

### 5. `@parallel` - Simple Decorator

**Best for**: Simple cases without configuration

```python
@parallel
async def search_ingredients(ingredients):
    return [search_ingredient(ingredient) for ingredient in ingredients]

results = await search_ingredients(ingredients)
```

## Real-World Example

Here's how it's used in the API:

```python
# Before (manual asyncio.gather)
async def search_stores_old(ingredients):
    responses = await asyncio.gather(
        *[search_ingredient(ingredient) for ingredient in ingredients],
        return_exceptions=True
    )
    return responses

# After (using parallel utilities)
from app.utils.parallel_utils import AsyncMap

async def search_stores_new(ingredients):
    responses = await AsyncMap.map(
        search_ingredient,
        ingredients,
        max_concurrency=3,    # Be nice to APIs
        delay=0.5,           # Rate limiting
        return_exceptions=True
    )
    return responses
```

## Advanced Features

### Rate Limiting

Add delays between requests to avoid overwhelming APIs:

```python
@run_parallel_comprehension(delay=0.5)  # 500ms between requests
def search_with_rate_limit(ingredients):
    return [search_ingredient(ingredient) for ingredient in ingredients]
```

### Concurrency Control

Limit the number of simultaneous operations:

```python
@run_parallel_comprehension(max_concurrency=3)  # Max 3 concurrent
def search_with_limit(ingredients):
    return [search_ingredient(ingredient) for ingredient in ingredients]
```

### Error Handling

Control how exceptions are handled:

```python
# Return exceptions as results (default)
@run_parallel_comprehension(return_exceptions=True)
def search_with_errors(ingredients):
    return [search_ingredient(ingredient) for ingredient in ingredients]

# This will return a list where some items might be Exception objects
results = await search_with_errors(ingredients)

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Error processing item {i}: {result}")
    else:
        print(f"Success: {result}")
```

### Context Manager Style

For more complex scenarios:

```python
from app.utils.parallel_utils import ParallelComprehension

async def complex_search(ingredients):
    async with ParallelComprehension(max_concurrency=3, delay=0.1) as p:
        tasks = [search_ingredient(ingredient) for ingredient in ingredients]
        results = await p.run(tasks)
    return results
```

## Performance Comparison

Typical performance gains:

| Method | 5 items (0.5s each) | Speedup |
|--------|---------------------|---------|
| Sequential | 2.5 seconds | 1x |
| Parallel (unlimited) | 0.5 seconds | 5x |
| Parallel (max_concurrency=3) | 1.0 seconds | 2.5x |
| Parallel with delay=0.1s | 0.9 seconds | 2.8x |

## Best Practices

1. **Use concurrency limits** for external APIs to avoid rate limiting
2. **Add delays** when making many requests to the same service
3. **Enable exception handling** to prevent one failure from stopping all tasks
4. **Choose the right method** for your use case:
   - Use `@run_parallel_comprehension()` for list comprehensions
   - Use `AsyncMap.map()` for functional style
   - Use `gather_with_limit()` when you need direct control

## Migration from Manual asyncio.gather

Replace this:
```python
results = await asyncio.gather(
    *[func(item) for item in items],
    return_exceptions=True
)
```

With this:
```python
@run_parallel_comprehension(return_exceptions=True)
def parallel_func(items):
    return [func(item) for item in items]

results = await parallel_func(items)
```

Or this:
```python
results = await AsyncMap.map(func, items, return_exceptions=True)
```