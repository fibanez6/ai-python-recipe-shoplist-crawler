#!/usr/bin/env python3
"""
Simple test runner for StorageManager tests.
Run this script to test the storage manager functionality.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config.logging_config import get_logger, setup_logging
from app.manager.storage_manager import JOBLIB_AVAILABLE, StorageManager
from app.models import Ingredient, Product, QuantityUnit, Recipe


def run_basic_storage_tests():
    """Run basic storage functionality tests."""
    
    # Setup logging
    setup_logging(debug=True)
    logger = get_logger(__name__)
    
    logger.info("🧪 Running Basic StorageManager Tests")
    logger.info("=" * 50)
    
    # Create temporary storage for testing
    test_storage_dir = Path("./test_storage_output")
    storage = StorageManager(test_storage_dir)
    
    try:
        # Test 1: Create sample objects
        logger.info("📦 Creating sample objects...")
        
        ingredient = Ingredient(
            name="chicken breast",
            quantity=1.5,
            unit=QuantityUnit.POUND,
            original_text="1.5 lbs boneless chicken breast",
            category="meat",
            notes="organic, free-range"
        )
        
        recipe = Recipe(
            title="Simple Grilled Chicken",
            url="https://example.com/grilled-chicken",
            description="A healthy grilled chicken recipe",
            servings=4,
            prep_time="10 minutes",
            cook_time="15 minutes",
            ingredients=[ingredient],
            instructions=[
                "Preheat grill to medium-high",
                "Season chicken with salt and pepper",
                "Grill 6-7 minutes per side",
                "Let rest 5 minutes before serving"
            ]
        )
        
        product = Product(
            name="Organic Chicken Breast - Family Pack",
            ingredient="chicken breast",
            price=8.99,
            store="Whole Foods",
            brand="Bell & Evans",
            size="1.5 lbs",
            unit_price=5.99,
            availability=True
        )
        
        logger.info("✅ Sample objects created successfully")
        
        # Test 2: JSON Serialization
        logger.info("\n🔄 Testing JSON serialization...")
        
        recipe_metadata = storage.save(recipe, "test_recipe", "json")
        ingredient_metadata = storage.save(ingredient, "test_ingredient", "json")
        
        if recipe_metadata and ingredient_metadata:
            logger.info("✅ JSON save successful")
            
            # Load back
            recipe_loaded = storage.load(recipe, "test_recipe", "json", model_class=Recipe)
            ingredient_loaded = storage.load(ingredient, "test_ingredient", "json", model_class=Ingredient)
            
            if recipe_loaded and ingredient_loaded:
                logger.info("✅ JSON load successful")
                logger.info(f"   Recipe: {recipe_loaded['object'].title}")
                logger.info(f"   Ingredient: {ingredient_loaded['object'].name}")
            else:
                logger.error("❌ JSON load failed")
        else:
            logger.error("❌ JSON save failed")
        
        # Test 3: Pickle Serialization
        logger.info("\n🥒 Testing Pickle serialization...")
        
        product_metadata = storage.save(product, "test_product", "pickle")
        
        if product_metadata:
            logger.info("✅ Pickle save successful")
            
            product_loaded = storage.load(product, "test_product", "pickle")
            
            if product_loaded:
                logger.info("✅ Pickle load successful")
                logger.info(f"   Product: {product_loaded['object'].name}")
            else:
                logger.error("❌ Pickle load failed")
        else:
            logger.error("❌ Pickle save failed")
        
        # Test 4: String Serialization
        logger.info("\n📝 Testing String serialization...")
        
        test_string = "This is a test string for storage verification"
        string_metadata = storage.save(test_string, "test_string", "string")
        
        if string_metadata:
            logger.info("✅ String save successful")
            
            string_loaded = storage.load(test_string, "test_string", "string")
            
            if string_loaded:
                logger.info("✅ String load successful")
                logger.info(f"   String: {string_loaded['object'][:30]}...")
            else:
                logger.error("❌ String load failed")
        else:
            logger.error("❌ String save failed")
        
        # Test 5: Complex Data Structure
        logger.info("\n🏗️ Testing complex data structure...")
        
        complex_data = {
            "recipes": [recipe],
            "products": [product],
            "ingredients": [ingredient],
            "metadata": {
                "version": "1.0",
                "created_by": "test_runner",
                "item_count": 3
            }
        }
        
        complex_metadata = storage.save(complex_data, "complex_test", "pickle")
        
        if complex_metadata:
            logger.info("✅ Complex data save successful")
            
            complex_loaded = storage.load(complex_data, "complex_test", "pickle")
            
            if complex_loaded:
                logger.info("✅ Complex data load successful")
                loaded_obj = complex_loaded['object']
                logger.info(f"   Recipes: {len(loaded_obj['recipes'])}")
                logger.info(f"   Products: {len(loaded_obj['products'])}")
                logger.info(f"   Version: {loaded_obj['metadata']['version']}")
            else:
                logger.error("❌ Complex data load failed")
        else:
            logger.error("❌ Complex data save failed")
        
        # Test 6: Storage Statistics
        logger.info("\n📊 Storage statistics...")
        stats = storage.get_stats()
        logger.info(f"   Files: {stats['entries']}")
        logger.info(f"   Total size: {stats['total_size']} bytes")
        logger.info(f"   Folder: {stats['folder']}")
        
        # Test 7: Auto-detection of format
        logger.info("\n🔍 Testing auto-detection of format...")
        
        # Save recipe with JSON
        storage.save(recipe, "auto_detect_test", "json")
        
        # Load without specifying format (should auto-detect)
        auto_loaded = storage.load(recipe, "auto_detect_test", model_class=Recipe)
        
        if auto_loaded:
            logger.info("✅ Auto-detection successful")
            logger.info(f"   Detected format: {auto_loaded.get('data_format', 'unknown')}")
        else:
            logger.error("❌ Auto-detection failed")
        
        logger.info("\n🎉 All tests completed!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        logger.info("\n🧹 Cleaning up test files...")
        try:
            removed_count = storage.clear()
            logger.info(f"   Removed {removed_count} files")
        except Exception as e:
            logger.warning(f"   Cleanup error: {e}")


def run_error_handling_tests():
    """Test error handling scenarios."""
    
    logger = get_logger(__name__)
    logger.info("\n⚠️ Testing Error Handling")
    logger.info("=" * 30)
    
    test_storage_dir = Path("./test_storage_errors")
    storage = StorageManager(test_storage_dir)
    
    try:
        # Test 1: Loading non-existent file
        logger.info("Testing load of non-existent file...")
        
        fake_recipe = Recipe(title="Fake", url="http://fake.com", ingredients=[])
        result = storage.load(fake_recipe, "non_existent", "json", model_class=Recipe)
        
        if result is None:
            logger.info("✅ Correctly handled non-existent file")
        else:
            logger.warning("⚠️ Unexpected result for non-existent file")
        
        # Test 2: Invalid serialization format
        logger.info("Testing invalid serialization format...")
        
        try:
            storage.save(fake_recipe, "test", "invalid_format")
            logger.error("❌ Should have raised ValueError")
        except ValueError:
            logger.info("✅ Correctly raised ValueError for invalid format")
        
        # Test 3: JSON load without model class
        logger.info("Testing JSON load without model class...")
        
        # First save something
        storage.save(fake_recipe, "test_no_model", "json")
        
        try:
            storage.load(fake_recipe, "test_no_model", "json")  # Missing model_class
            logger.error("❌ Should have raised ValueError")
        except ValueError:
            logger.info("✅ Correctly raised ValueError for missing model_class")
        
        logger.info("✅ Error handling tests completed")
        
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
    
    finally:
        # Cleanup
        try:
            storage.clear()
        except:
            pass


def demonstrate_practical_usage():
    """Demonstrate practical usage scenarios."""
    
    logger = get_logger(__name__)
    logger.info("\n💡 Practical Usage Examples")
    logger.info("=" * 35)
    
    test_storage_dir = Path("./practical_storage_demo")
    storage = StorageManager(test_storage_dir)
    
    try:
        # Scenario 1: Recipe Collection Management
        logger.info("📚 Scenario 1: Recipe Collection Management")
        
        # Create multiple recipes
        recipes = []
        for i in range(3):
            recipe = Recipe(
                title=f"Recipe Collection Item {i+1}",
                url=f"https://example.com/recipe-{i+1}",
                description=f"Description for recipe {i+1}",
                servings=4,
                ingredients=[
                    Ingredient(
                        name=f"ingredient_{i+1}",
                        quantity=float(i+1),
                        unit=QuantityUnit.CUP,
                        original_text=f"{i+1} cups ingredient_{i+1}"
                    )
                ],
                instructions=[f"Step {j}" for j in range(1, 4)]
            )
            recipes.append(recipe)
        
        # Save recipe collection
        collection_metadata = storage.save(recipes, "recipe_collection", "json")
        logger.info(f"   Saved collection: {collection_metadata['data_size']}")
        
        # Load and verify
        loaded_collection = storage.load(recipes, "recipe_collection", "json")
        if loaded_collection:
            logger.info(f"   Loaded {len(loaded_collection['object'])} recipes")
        
        # Scenario 2: Caching Expensive Operations
        logger.info("\n⚡ Scenario 2: Caching Expensive Operations")
        
        # Simulate expensive computation result
        expensive_result = {
            "computation_id": "complex_analysis_001",
            "results": [i**2 for i in range(100)],  # Simulate complex calculation
            "metadata": {
                "computation_time": 5.7,
                "algorithm": "advanced_optimization",
                "parameters": {"iterations": 1000, "tolerance": 0.001}
            }
        }
        
        # Cache the result
        cache_metadata = storage.save(expensive_result, "computation_cache", "pickle")
        logger.info(f"   Cached result: {cache_metadata['data_size']}")
        
        # Retrieve from cache
        cached_result = storage.load(expensive_result, "computation_cache", "pickle")
        if cached_result:
            result_obj = cached_result['object']
            logger.info(f"   Retrieved cached computation with {len(result_obj['results'])} data points")
        
        # Scenario 3: Configuration Backup
        logger.info("\n⚙️ Scenario 3: Configuration Backup")
        
        # Simulate application configuration
        app_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "recipe_db"
            },
            "storage": {
                "enable_saving": True,
                "enable_loading": True,
                "cache_size": "100MB"
            },
            "features": {
                "ai_analysis": True,
                "price_optimization": True,
                "multi_store_search": False
            }
        }
        
        # Backup configuration
        config_metadata = storage.save(app_config, "app_config_backup", "json")
        logger.info(f"   Backed up config: {config_metadata['data_size']}")
        
        # Restore configuration
        restored_config = storage.load(app_config, "app_config_backup", "json")
        if restored_config:
            config_obj = restored_config['object']
            logger.info(f"   Restored config with {len(config_obj)} sections")
        
        logger.info("\n🎯 Practical examples completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Practical examples failed: {e}")
    
    finally:
        # Cleanup
        try:
            storage.clear()
            logger.info("🧹 Cleaned up practical demo files")
        except:
            pass


if __name__ == "__main__":
    print("🚀 StorageManager Test Runner")
    print("=" * 50)
    
    success = True
    
    # Run all test suites
    success &= run_basic_storage_tests()
    run_error_handling_tests()
    demonstrate_practical_usage()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests completed successfully!")
        print("\n💡 Usage Summary:")
        print("   • Use JSON for Pydantic models (human-readable)")
        print("   • Use Pickle for complex Python objects")
        print("   • Use String for simple text data")
        print("   • Auto-detection works when loading")
        print("   • Always handle errors gracefully")
    else:
        print("❌ Some tests failed. Check the logs above.")
        sys.exit(1)