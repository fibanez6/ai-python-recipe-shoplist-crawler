"""Utility decorators and functions for parallel execution using asyncio."""

import asyncio
import functools
import inspect
from typing import Any, Awaitable, Callable, Generator, Iterable, List, TypeVar, Union

T = TypeVar('T')


class ParallelExecution:
    """Decorator for running functions in parallel using asyncio.gather."""
    
    def __init__(self, max_concurrency: int = None, return_exceptions: bool = True, delay: float = 0.0):
        """
        Initialize the parallel execution decorator.
        
        Args:
            max_concurrency: Maximum number of concurrent executions (None for unlimited)
            return_exceptions: Whether to return exceptions as results instead of raising
            delay: Delay in seconds between starting each task (for rate limiting)
        """
        self.max_concurrency = max_concurrency
        self.return_exceptions = return_exceptions
        self.delay = delay

    def __call__(self, func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[List[T]]]:
        """
        Decorator that wraps a function to run in parallel.
        
        The decorated function should return an async generator or iterable of coroutines.
        """
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> List[T]:
            # Get the generator/iterable from the original function
            result = func(*args, **kwargs)
            
            # Handle different types of results
            if inspect.isasyncgen(result):
                # Async generator - collect all items
                tasks = [item async for item in result]
            elif inspect.isgenerator(result):
                # Regular generator - collect all items
                tasks = list(result)
            elif hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                # Regular iterable (but not string/bytes)
                tasks = list(result)
            else:
                # Single coroutine
                tasks = [result]
            
            # Execute using gather_with_limit which handles delays and concurrency
            return await gather_with_limit(
                tasks,
                max_concurrency=self.max_concurrency,
                return_exceptions=self.return_exceptions,
                delay=self.delay
            )
        
        return wrapper


def run_in_parallel(max_concurrency: int = None, return_exceptions: bool = True, delay: float = 0.0):
    """
    Decorator factory for parallel execution.
    
    Usage:
        @run_in_parallel(max_concurrency=5, delay=0.1)
        async def search_ingredients(ingredients):
            return [search_ingredient(ingredient) for ingredient in ingredients]
    
    Alternative usage (more elegant syntax):
        @run_in_parallel()
        async def search_all_ingredients(ingredients):
            return (search_ingredient(ingredient) for ingredient in ingredients)
    
    Args:
        max_concurrency: Maximum number of concurrent executions
        return_exceptions: Whether to return exceptions as results
        delay: Delay between starting tasks (for rate limiting)
    """
    return ParallelExecution(max_concurrency, return_exceptions, delay)


def parallel_comprehension(iterable_func: Callable, async_func: Callable, **kwargs):
    """
    Execute a comprehension-style parallel operation.
    
    This allows syntax like:
        results = await parallel_comprehension(
            lambda: ingredients,
            search_ingredient,
            max_concurrency=3,
            delay=0.5
        )
    
    Which is equivalent to:
        [search_ingredient(ingredient) for ingredient in ingredients]
    but executed in parallel.
    """
    async def execute():
        items = iterable_func() if callable(iterable_func) else iterable_func
        return await AsyncMap.map(async_func, items, **kwargs)
    
    return execute()


async def gather_with_limit(
    tasks: Iterable[Awaitable[T]], 
    max_concurrency: int = None, 
    return_exceptions: bool = True,
    delay: float = 0.0
) -> List[T]:
    """
    Execute tasks in parallel with optional concurrency limit and delay.
    
    Args:
        tasks: Iterable of awaitable tasks
        max_concurrency: Maximum concurrent tasks (None for unlimited)
        return_exceptions: Whether to return exceptions as results
        delay: Delay between starting each task
    
    Returns:
        List of results in the same order as input tasks
    """
    task_list = list(tasks)
    
    # Add delays if specified
    if delay > 0:
        async def delayed_task(task, delay_time):
            if delay_time > 0:
                await asyncio.sleep(delay_time)
            return await task
        
        task_list = [
            delayed_task(task, i * delay) 
            for i, task in enumerate(task_list)
        ]
    
    if max_concurrency and len(task_list) > max_concurrency:
        results = []
        for i in range(0, len(task_list), max_concurrency):
            batch = task_list[i:i + max_concurrency]
            batch_results = await asyncio.gather(*batch, return_exceptions=return_exceptions)
            results.extend(batch_results)
        return results
    else:
        return await asyncio.gather(*task_list, return_exceptions=return_exceptions)


# Convenience decorator for simple cases
def parallel(func):
    """
    Simple decorator for parallel execution without configuration.
    
    Usage:
        @parallel
        async def process_items(items):
            return [process_item(item) for item in items]
    """
    return run_in_parallel()(func)


class ParallelComprehension:
    """
    Context manager that enables parallel comprehension syntax.
    
    Usage:
        async with ParallelComprehension(max_concurrency=3, delay=0.5) as p:
            results = await p.run([search_ingredient(ingredient) for ingredient in ingredients])
    
    Or using the function wrapper:
        @run_parallel_comprehension(max_concurrency=3, delay=0.5)
        def search_all(ingredients):
            return [search_ingredient(ingredient) for ingredient in ingredients]
        
        results = await search_all(ingredients)
    """
    
    def __init__(self, max_concurrency: int = None, return_exceptions: bool = True, delay: float = 0.0):
        self.max_concurrency = max_concurrency
        self.return_exceptions = return_exceptions
        self.delay = delay
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def run(self, tasks: List[Awaitable[T]]) -> List[T]:
        """Execute a list of tasks in parallel."""
        return await gather_with_limit(
            tasks,
            max_concurrency=self.max_concurrency,
            return_exceptions=self.return_exceptions,
            delay=self.delay
        )


def run_parallel_comprehension(max_concurrency: int = None, return_exceptions: bool = True, delay: float = 0.0):
    """
    Decorator that enables parallel execution of comprehensions.
    
    Usage:
        @run_parallel_comprehension(max_concurrency=3, delay=0.5)
        def search_all_ingredients(ingredients):
            return [search_ingredient(ingredient) for ingredient in ingredients]
        
        # Call it
        results = await search_all_ingredients(ingredients)
    
    This is the closest to your requested syntax:
        @run_parallel_comprehension()
        def parallel_search(ingredients):
            return [search_ingredient(ingredient) for ingredient in ingredients]
    """
    def decorator(func: Callable[..., List[Awaitable[T]]]) -> Callable[..., Awaitable[List[T]]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> List[T]:
            # Get the list of tasks from the original function
            tasks = func(*args, **kwargs)
            
            # Execute them in parallel
            return await gather_with_limit(
                tasks,
                max_concurrency=max_concurrency,
                return_exceptions=return_exceptions,
                delay=delay
            )
        
        return wrapper
    return decorator


class AsyncMap:
    """Utility class for mapping async functions over iterables in parallel."""
    
    @staticmethod
    async def map(
        func: Callable[[T], Awaitable[Any]], 
        iterable: Iterable[T],
        max_concurrency: int = None,
        return_exceptions: bool = True,
        delay: float = 0.0
    ) -> List[Any]:
        """
        Map an async function over an iterable in parallel.
        
        Usage:
            results = await AsyncMap.map(search_ingredient, ingredients, max_concurrency=5)
        """
        tasks = [func(item) for item in iterable]
        return await gather_with_limit(
            tasks, 
            max_concurrency=max_concurrency,
            return_exceptions=return_exceptions,
            delay=delay
        )


# Example usage functions for reference
async def example_usage():
    """Example usage of the parallel execution utilities."""
    
    # Example 1: Using the decorator
    @run_in_parallel(max_concurrency=5, delay=0.1)
    async def search_ingredients_parallel(ingredients):
        """Search for ingredients in parallel with concurrency limit."""
        return [search_ingredient(ingredient) for ingredient in ingredients]
    
    # Example 2: Using AsyncMap
    async def search_with_map(ingredients):
        """Search using AsyncMap utility."""
        return await AsyncMap.map(
            search_ingredient, 
            ingredients, 
            max_concurrency=5, 
            delay=0.1
        )
    
    # Example 3: Using gather_with_limit directly
    async def search_with_gather(ingredients):
        """Search using gather_with_limit directly."""
        tasks = [search_ingredient(ingredient) for ingredient in ingredients]
        return await gather_with_limit(
            tasks, 
            max_concurrency=5, 
            delay=0.1
        )


async def search_ingredient(ingredient):
    """Mock function for examples."""
    await asyncio.sleep(0.1)  # Simulate async work
    return f"Result for {ingredient}"