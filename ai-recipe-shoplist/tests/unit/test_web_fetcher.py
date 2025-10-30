#!/usr/bin/env python3
"""
Test script for the web fetcher service.
Demonstrates fetching web content with caching and cleaning.
"""

import asyncio
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.logging_config import get_logger, setup_logging
from app.services.web_fetcher import get_web_fetcher


async def test_web_fetcher():
    """Test the web fetcher service with a real recipe URL."""
    
    # Setup logging
    setup_logging(debug=True)
    logger = get_logger(__name__)
    
    logger.info("Testing Web Fetcher Service")
    logger.info("=" * 40)
    
    # Get fetcher instance
    fetcher = get_web_fetcher()
    
    # Test URL (a simple recipe site)
    test_url = "https://www.allrecipes.com/recipe/213742/cheesy-chicken-broccoli-casserole/"
    
    try:
        # First fetch (should hit the network)
        logger.info("First fetch (from network):")
        result1 = await fetcher.fetch_html_content(test_url)
        
        logger.info(f"  URL: {result1['url']}")
        logger.info(f"  Status: {result1['status_code']}")
        logger.info(f"  Size: {result1['size']} bytes")
        logger.info(f"  From cache: {result1['from_cache']}")
        logger.info(f"  Content preview: {result1['content'][:100]}...")
        if 'cleaned_content' in result1:
            logger.info(f"  Cleaned size: {len(result1['cleaned_content'])} bytes")
        
        # Second fetch (should hit the cache)
        logger.info("\nSecond fetch (from cache):")
        result2 = await fetcher.fetch_html_content(test_url)
        
        logger.info(f"  From cache: {result2['from_cache']}")
        logger.info(f"  Size: {result2['size']} bytes")
        
        # Show cache stats
        logger.info("\nCache statistics:")
        stats = fetcher.get_cache_stats()
        logger.info(f"  Entries: {stats['entries']}")
        logger.info(f"  Total size: {stats['total_size']} bytes")
        logger.info(f"  TTL: {stats['ttl_seconds']} seconds")
        
        # Test cache clearing
        logger.info("\nClearing cache...")
        fetcher.clear_cache()
        
        stats_after = fetcher.get_cache_stats()
        logger.info(f"  Entries after clear: {stats_after['entries']}")
        
        logger.info("\n✅ Web fetcher test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

async def test_multiple_urls():
    """Test fetching multiple URLs."""
    fetcher = get_web_fetcher()
    logger = get_logger(__name__)
    
    urls = [
        "https://www.example.com",
        "https://httpbin.org/json",
        "https://httpbin.org/html"
    ]
    
    logger.info("Testing multiple URLs:")
    
    for url in urls:
        try:
            result = await fetcher.fetch_url(url)
            logger.info(f"  {url}: {result['status_code']} - {result['size']} bytes")
        except Exception as e:
            logger.warning(f"  {url}: Failed - {e}")

async def main():
    """Run all tests."""
    try:
        await test_web_fetcher()
        print("\n" + "-"*50 + "\n")
        await test_multiple_urls()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())