#!/usr/bin/env python3
"""
Test script for the store configuration system.
Demonstrates store configs, regional filtering, and URL generation.
"""

import asyncio
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.logging_config import get_logger, setup_logging
from app.config.store_config import (
    StoreRegion,
    get_all_store_ids,
    get_store_config,
    get_store_display_names,
    get_stores_by_region,
)
from app.models import Ingredient
from app.services.store_crawler import store_crawler


async def test_store_configuration():
    """Test the store configuration system."""
    logger = get_logger(__name__)
    
    logger.info("Testing Store Configuration System")
    logger.info("=" * 50)
    
    # Test 1: Show all available stores
    logger.info("1. All Available Stores:")
    all_stores = get_all_store_ids()
    display_names = get_store_display_names()
    
    for store_id in all_stores:
        logger.info(f"  - {store_id}: {display_names[store_id]}")
    
    print()
    
    # Test 2: Show stores by region
    logger.info("2. Stores by Region:")
    for region in StoreRegion:
        stores = get_stores_by_region(region)
        logger.info(f"  {region.value}: {[s.name for s in stores]}")
    
    print()
    
    # Test 3: Show detailed store configuration
    logger.info("3. Detailed Store Configuration (Coles):")
    coles_config = get_store_config("coles")
    if coles_config:
        logger.info(f"  Store ID: {coles_config.store_id}")
        logger.info(f"  Display Name: {coles_config.display_name}")
        logger.info(f"  Base URL: {coles_config.base_url}")
        logger.info(f"  Search URL: {coles_config.search_url}")
        logger.info(f"  Price Multiplier: {coles_config.price_multiplier}")
        logger.info(f"  Rate Limit: {coles_config.rate_limit_delay}s")
        logger.info(f"  Supports Delivery: {coles_config.supports_delivery}")
        
        # Test URL generation
        search_url = coles_config.get_search_url("tomato sauce")
        product_url = coles_config.get_product_url("heinz-tomato-sauce-500ml")
        logger.info(f"  Sample Search URL: {search_url}")
        logger.info(f"  Sample Product URL: {product_url}")
    
    print()
    
    # Test 4: Test store crawler with configuration
    logger.info("4. Testing Store Crawler with Configuration:")
    ingredients = [
        Ingredient(name="tomato", original_text="2 tomatoes"),
        Ingredient(name="bread", original_text="1 loaf of bread")
    ]
    
    # Get store info
    store_info = store_crawler.get_all_stores_info()
    logger.info("  Available stores:")
    for store_id, info in store_info.items():
        logger.info(f"    {store_id}: {info['display_name']} (Price multiplier: {info['price_multiplier']})")
    
    # Test search
    logger.info("\n  Testing search...")
    results = await store_crawler.search_all_stores(ingredients, ["coles", "aldi"])
    
    for store, store_results in results.items():
        logger.info(f"    {store}:")
        for result in store_results:
            logger.info(f"      {result.ingredient_name}: {len(result.products)} products found")
            if result.products:
                sample_product = result.products[0]
                logger.info(f"        Sample: {sample_product.title} - ${sample_product.price}")
                logger.info(f"        URL: {sample_product.url}")
    
    print()

async def test_regional_switching():
    """Test switching between regions."""
    logger = get_logger(__name__)
    
    logger.info("5. Testing Regional Switching:")
    
    # Test Australian stores
    logger.info("  Australian stores:")
    store_crawler.set_region(StoreRegion.AUSTRALIA)
    au_stores = store_crawler.get_available_stores()
    logger.info(f"    {au_stores}")
    
    # Test US stores
    logger.info("  US stores:")
    store_crawler.set_region(StoreRegion.UNITED_STATES)
    us_stores = store_crawler.get_available_stores()
    logger.info(f"    {us_stores}")
    
    # Get detailed info for a US store
    if us_stores:
        walmart_info = store_crawler.get_store_info("walmart")
        if walmart_info:
            logger.info(f"    Walmart info: {walmart_info}")
    
    # Switch back to Australia
    store_crawler.set_region(StoreRegion.AUSTRALIA)
    logger.info("  Switched back to Australia")
    
    print()

def test_url_generation():
    """Test URL generation for different stores."""
    logger = get_logger(__name__)
    
    logger.info("6. Testing URL Generation:")
    
    test_queries = ["organic tomatoes", "free range eggs", "gluten free bread"]
    test_stores = ["coles", "woolworths", "aldi", "walmart"]
    
    for store_id in test_stores:
        config = get_store_config(store_id)
        if config:
            logger.info(f"  {config.display_name}:")
            for query in test_queries:
                search_url = config.get_search_url(query)
                logger.info(f"    '{query}': {search_url}")
    
    print()

def main():
    """Run all store configuration tests."""
    setup_logging(debug=True)
    logger = get_logger(__name__)
    
    logger.info("Store Configuration Test Suite")
    logger.info("=" * 60)
    
    try:
        asyncio.run(test_store_configuration())
        asyncio.run(test_regional_switching())
        test_url_generation()
        
        logger.info("✅ All store configuration tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main()