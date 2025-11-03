#!/usr/bin/env python3
"""
Comprehensive test suite for StorageManager.
Tests all serialization methods and functionality.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.config.logging_config import get_logger, setup_logging
from app.manager.storage_manager import StorageManager, get_storage_manager
from app.models import Ingredient, Product, QuantityUnit, Recipe


class TestStorageManager(unittest.TestCase):
    """Test cases for StorageManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        self.storage = StorageManager(self.test_dir)
        
        # Create sample test objects
        self.sample_ingredient = Ingredient(
            name="tomatoes",
            quantity=2.0,
            unit=QuantityUnit.PIECE,
            original_text="2 fresh tomatoes",
            category="produce",
            alternatives=["cherry tomatoes", "canned tomatoes"],
            notes="fresh and ripe",
            brand_preference="Organic"
        )
        
        self.sample_recipe = Recipe(
            title="Test Recipe",
            url="https://example.com/test-recipe",
            description="A test recipe for unit testing",
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            ingredients=[self.sample_ingredient],
            instructions=["Step 1: Test", "Step 2: Verify", "Step 3: Complete"]
        )
        
        self.sample_product = Product(
            name="Test Product",
            ingredient="tomatoes",
            price=2.99,
            store="Test Store",
            quantity=1,
            brand="Test Brand",
            size="1 lb",
            unit_price=2.99,
            availability=True,
            ia_reasoning="Perfect match for test requirements"
        )
        
        # Setup logging for tests
        setup_logging(debug=True)
        self.logger = get_logger(__name__)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove all test files
        if self.test_dir.exists():
            for file in self.test_dir.rglob("*"):
                if file.is_file():
                    file.unlink()
            try:
                self.test_dir.rmdir()
            except OSError:
                pass  # Directory not empty
    
    # ===== Basic Functionality Tests =====
    
    def test_storage_manager_initialization(self):
        """Test StorageManager initialization."""
        self.assertTrue(self.test_dir.exists())
        self.assertEqual(self.storage.base_path, self.test_dir)
        self.assertTrue(self.storage.enable_saving)
        self.assertTrue(self.storage.enable_loading)
    
    def test_object_to_str_conversion(self):
        """Test object to string conversion."""
        # Test with Pydantic model
        obj_str = self.storage._object_to_str(self.sample_recipe)
        self.assertIsInstance(obj_str, str)
        self.assertIn("Test Recipe", obj_str)
        
        # Test with regular dict
        test_dict = {"key": "value", "number": 42}
        dict_str = self.storage._object_to_str(test_dict)
        self.assertIsInstance(dict_str, str)
        
        # Test with simple string
        simple_str = self.storage._object_to_str("test string")
        self.assertEqual(simple_str, "test string")
    
    def test_hash_generation(self):
        """Test hash generation for objects."""
        obj_str = self.storage._object_to_str(self.sample_recipe)
        hash1 = self.storage._get_hash(obj_str, "test_alias")
        hash2 = self.storage._get_hash(obj_str, "test_alias")
        hash3 = self.storage._get_hash(obj_str, "different_alias")
        
        # Same object and alias should generate same hash
        self.assertEqual(hash1, hash2)
        
        # Different alias should generate different hash
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be a valid MD5 hex string
        self.assertEqual(len(hash1), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1))
    
    # ===== JSON Serialization Tests =====
    
    def test_save_load_pydantic_json(self):
        """Test saving and loading Pydantic objects as JSON."""
        # Save the recipe
        saved_path = self.storage.save_pydantic_as_json(self.sample_recipe, "test_recipe")
        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.suffix, ".json")
        
        # Load the recipe back
        loaded_recipe = self.storage.load_pydantic_from_json("test_recipe", Recipe)
        
        # Verify the loaded recipe matches the original
        self.assertEqual(loaded_recipe.title, self.sample_recipe.title)
        self.assertEqual(loaded_recipe.url, self.sample_recipe.url)
        self.assertEqual(loaded_recipe.servings, self.sample_recipe.servings)
        self.assertEqual(len(loaded_recipe.ingredients), len(self.sample_recipe.ingredients))
        self.assertEqual(loaded_recipe.ingredients[0].name, self.sample_ingredient.name)
    
    def test_json_file_not_found(self):
        """Test loading non-existent JSON file."""
        with self.assertRaises(FileNotFoundError):
            self.storage.load_pydantic_from_json("non_existent", Recipe)
    
    def test_save_load_regular_object_as_json(self):
        """Test saving regular objects as JSON."""
        test_data = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        saved_path = self.storage.save_pydantic_as_json(test_data, "test_data")
        self.assertTrue(saved_path.exists())
        
        # Manually load and verify JSON content
        with open(saved_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data, test_data)
    
    # ===== Pickle Serialization Tests =====
    
    def test_save_load_pickle(self):
        """Test saving and loading objects with pickle."""
        # Save the product
        saved_path = self.storage.save_with_pickle(self.sample_product, "test_product")
        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.suffix, ".pkl")
        
        # Load the product back
        loaded_product = self.storage.load_with_pickle("test_product")
        
        # Verify the loaded product matches the original
        self.assertEqual(loaded_product.name, self.sample_product.name)
        self.assertEqual(loaded_product.price, self.sample_product.price)
        self.assertEqual(loaded_product.store, self.sample_product.store)
    
    def test_pickle_complex_objects(self):
        """Test pickling complex objects with references."""
        complex_data = {
            "recipes": [self.sample_recipe],
            "products": [self.sample_product],
            "metadata": {
                "created_at": datetime.now(),
                "version": "1.0",
                "tags": ["test", "unit testing"],
                "counts": {"recipes": 1, "products": 1}
            },
            "nested_list": [[1, 2, 3], ["a", "b", "c"]]
        }
        
        saved_path = self.storage.save_with_pickle(complex_data, "complex_data")
        loaded_data = self.storage.load_with_pickle("complex_data")
        
        # Verify complex data structure
        self.assertEqual(len(loaded_data["recipes"]), 1)
        self.assertEqual(loaded_data["recipes"][0].title, self.sample_recipe.title)
        self.assertEqual(len(loaded_data["products"]), 1)
        self.assertEqual(loaded_data["metadata"]["version"], "1.0")
        self.assertEqual(loaded_data["nested_list"][0], [1, 2, 3])
        self.assertIsInstance(loaded_data["metadata"]["created_at"], datetime)
    
    def test_pickle_file_not_found(self):
        """Test loading non-existent pickle file."""
        with self.assertRaises(FileNotFoundError):
            self.storage.load_with_pickle("non_existent")
    
    # ===== Joblib Serialization Tests =====
    
    def test_save_load_joblib(self):
        """Test saving and loading objects with joblib."""
        # Create large dataset to test joblib efficiency
        large_dataset = {
            "recipes": [self.sample_recipe] * 10,
            "products": [self.sample_product] * 20,
            "numbers": list(range(1000))
        }
        
        saved_path = self.storage.save_with_joblib(large_dataset, "large_dataset")
        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.suffix, ".joblib")
        
        loaded_data = self.storage.load_with_joblib("large_dataset")
        
        # Verify large dataset
        self.assertEqual(len(loaded_data["recipes"]), 10)
        self.assertEqual(len(loaded_data["products"]), 20)
        self.assertEqual(len(loaded_data["numbers"]), 1000)
        self.assertEqual(loaded_data["recipes"][0].title, self.sample_recipe.title)
    
    def test_joblib_file_not_found(self):
        """Test loading non-existent joblib file."""
        with self.assertRaises(FileNotFoundError):
            self.storage.load_with_joblib("non_existent")
    
    # ===== String Serialization Tests =====
    
    def test_save_load_string(self):
        """Test saving and loading plain strings."""
        test_string = "This is a test string with unicode characters: émojis 🚀 and símböls!"
        
        saved_path = self.storage.save_as_string(test_string, "test_string")
        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.suffix, ".txt")
        
        loaded_string = self.storage.load_as_string("test_string")
        self.assertEqual(loaded_string, test_string)
    
    def test_save_load_object_as_string(self):
        """Test saving objects as string representation."""
        saved_path = self.storage.save_object_as_string(self.sample_ingredient, "ingredient_str")
        self.assertTrue(saved_path.exists())
        
        # Load as JSON and reconstruct
        loaded_ingredient = self.storage.load_string_as_json("ingredient_str", Ingredient)
        self.assertEqual(loaded_ingredient.name, self.sample_ingredient.name)
        self.assertEqual(loaded_ingredient.quantity, self.sample_ingredient.quantity)
    
    def test_string_file_not_found(self):
        """Test loading non-existent string file."""
        with self.assertRaises(FileNotFoundError):
            self.storage.load_as_string("non_existent")
    
    # ===== Custom JSON Serialization Tests =====
    
    def test_custom_json_with_datetime(self):
        """Test custom JSON serialization with datetime objects."""
        def custom_encoder(obj):
            if isinstance(obj, datetime):
                return {"__datetime__": obj.isoformat()}
            return str(obj)
        
        def custom_decoder(data):
            """Recursively decode datetime objects from JSON."""
            if isinstance(data, dict):
                if "__datetime__" in data:
                    return datetime.fromisoformat(data["__datetime__"])
                else:
                    # Recursively decode nested dictionaries
                    return {k: custom_decoder(v) for k, v in data.items()}
            elif isinstance(data, list):
                # Recursively decode list items
                return [custom_decoder(item) for item in data]
            return data
        
        test_data = {
            "recipe": self.sample_recipe.model_dump(),  # Use model_dump instead of deprecated dict()
            "created_at": datetime.now(),
            "tags": ["test", "datetime"]
        }
        
        saved_path = self.storage.save_custom_json(test_data, "datetime_test", custom_encoder)
        loaded_data = self.storage.load_custom_json("datetime_test", custom_decoder)
        
        # Verify datetime was preserved
        self.assertIsInstance(loaded_data["created_at"], datetime)
        self.assertEqual(loaded_data["recipe"]["title"], self.sample_recipe.title)
    
    # ===== Metadata Tests =====
    
    def test_save_load_metadata(self):
        """Test metadata saving and loading."""
        filename = "test_metadata"
        file_path = self.test_dir / "test_file.json"
        alias = "test_alias"
        obj_size = 1024
        format_type = "json"
        
        # Save metadata
        metadata = self.storage._save_metadata(filename, file_path, alias, obj_size, format_type)
        
        # Verify metadata structure
        self.assertEqual(metadata["filename"], filename)
        self.assertEqual(metadata["alias"], alias)
        self.assertEqual(metadata["file_path"], str(file_path))
        self.assertIn("1024 bytes", metadata["data_size"])
        self.assertEqual(metadata["data_format"], format_type)
        self.assertIsInstance(metadata["timestamp"], float)
        
        # Load metadata back
        loaded_metadata = self.storage._load_metadata(filename)
        self.assertEqual(loaded_metadata["filename"], filename)
        self.assertEqual(loaded_metadata["alias"], alias)
    
    def test_metadata_file_not_found(self):
        """Test loading non-existent metadata file."""
        with self.assertRaises(FileNotFoundError):
            self.storage._load_metadata("non_existent")
    
    # ===== Generic Save/Load Tests =====
    
    def test_generic_save_load_json(self):
        """Test generic save/load with JSON format."""
        metadata = self.storage.save(self.sample_recipe, "recipe", "json")
        self.assertIsNotNone(metadata)
        self.assertIn("file_path", metadata)
        
        loaded_data = self.storage.load(self.sample_recipe, "recipe", "json", model_class=Recipe)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["object"].title, self.sample_recipe.title)
    
    def test_generic_save_load_pickle(self):
        """Test generic save/load with pickle format."""
        metadata = self.storage.save(self.sample_product, "product", "pickle")
        self.assertIsNotNone(metadata)
        
        loaded_data = self.storage.load(self.sample_product, "product", "pickle")
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["object"].name, self.sample_product.name)
    
    def test_generic_save_invalid_format(self):
        """Test generic save with invalid format."""
        with self.assertRaises(ValueError):
            self.storage.save(self.sample_recipe, "recipe", "invalid_format")
    
    def test_generic_load_auto_detect_format(self):
        """Test generic load with auto-detection of format."""
        # Save with explicit format
        self.storage.save(self.sample_ingredient, "ingredient", "json")
        
        # Load without specifying format (should auto-detect)
        loaded_data = self.storage.load(self.sample_ingredient, "ingredient", model_class=Ingredient)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["object"].name, self.sample_ingredient.name)
    
    def test_generic_load_json_without_model_class(self):
        """Test generic load JSON without model class should raise error."""
        self.storage.save(self.sample_recipe, "recipe", "json")
        
        with self.assertRaises(ValueError):
            self.storage.load(self.sample_recipe, "recipe", "json")  # Missing model_class
    
    # ===== Storage Management Tests =====
    
    def test_clear_storage(self):
        """Test clearing all storage files."""
        # Save some test files
        self.storage.save_pydantic_as_json(self.sample_recipe, "recipe1")
        self.storage.save_with_pickle(self.sample_product, "product1")
        self.storage.save_as_string("test", "string1")
        
        # Verify files exist
        files_before = list(self.test_dir.iterdir())
        self.assertGreater(len(files_before), 0)
        
        # Clear storage
        removed_count = self.storage.clear()
        self.assertGreater(removed_count, 0)
        
        # Verify files are removed
        if self.test_dir.exists():
            files_after = list(self.test_dir.iterdir())
            self.assertEqual(len(files_after), 0)
    
    def test_get_stats(self):
        """Test storage statistics."""
        # Initially empty
        stats = self.storage.get_stats()
        self.assertEqual(stats["entries"], 0)
        self.assertEqual(stats["total_size"], 0)
        self.assertTrue(stats["saving_enabled"])
        self.assertTrue(stats["loading_enabled"])
        
        # After saving some files
        self.storage.save_pydantic_as_json(self.sample_recipe, "recipe_stats")
        self.storage.save_with_pickle(self.sample_product, "product_stats")
        
        stats_after = self.storage.get_stats()
        self.assertGreater(stats_after["entries"], 0)
        self.assertGreater(stats_after["total_size"], 0)
    
    # ===== Disabled Storage Tests =====
    
    @patch('app.manager.storage_manager.STORAGE_SETTINGS')
    def test_disabled_saving(self, mock_settings):
        """Test behavior when saving is disabled."""
        mock_settings.enable_saving = False
        mock_settings.enable_loading = True
        mock_settings.base_path = self.test_dir
        
        disabled_storage = StorageManager(self.test_dir)
        result = disabled_storage.save(self.sample_recipe, "recipe", "json")
        
        self.assertEqual(result, {})
    
    @patch('app.manager.storage_manager.STORAGE_SETTINGS')
    def test_disabled_loading(self, mock_settings):
        """Test behavior when loading is disabled."""
        mock_settings.enable_saving = True
        mock_settings.enable_loading = False
        mock_settings.base_path = self.test_dir
        
        disabled_storage = StorageManager(self.test_dir)
        result = disabled_storage.load(self.sample_recipe, "recipe", "json")
        
        self.assertEqual(result, {})
    
    # ===== Error Handling Tests =====
    
    def test_save_io_error(self):
        """Test handling of IO errors during save."""
        # Create a read-only directory
        readonly_dir = self.test_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        readonly_storage = StorageManager(readonly_dir)
        
        try:
            result = readonly_storage.save(self.sample_recipe, "recipe", "json")
            # Should return None on IO error
            self.assertIsNone(result)
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)
    
    def test_load_corrupted_metadata(self):
        """Test handling of corrupted metadata files."""
        # Create corrupted metadata file
        corrupted_metadata_path = self.test_dir / "corrupted_metadata.json"
        with open(corrupted_metadata_path, 'w') as f:
            f.write("invalid json content {")
        
        with self.assertRaises(json.JSONDecodeError):
            self.storage._load_metadata("corrupted")
    
    def test_load_missing_data_file(self):
        """Test loading when metadata exists but data file is missing."""
        # Save an object first
        self.storage.save(self.sample_recipe, "recipe", "json")
        
        # Find and delete the data file but keep metadata
        obj_str = self.storage._object_to_str(self.sample_recipe)
        filename = self.storage._get_hash(obj_str, "recipe")
        data_file = self.test_dir / f"{filename}.json"
        data_file.unlink()
        
        # Try to load - should return None
        result = self.storage.load(self.sample_recipe, "recipe", "json", model_class=Recipe)
        self.assertIsNone(result)
    
    # ===== Global Storage Manager Tests =====
    
    def test_get_storage_manager_singleton(self):
        """Test that get_storage_manager returns a singleton."""
        manager1 = get_storage_manager()
        manager2 = get_storage_manager()
        
        # Should be the same instance
        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, StorageManager)


class TestStorageManagerIntegration(unittest.TestCase):
    """Integration tests for StorageManager with real scenarios."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.storage = StorageManager(self.test_dir)
        setup_logging(debug=False)  # Less verbose for integration tests
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        if self.test_dir.exists():
            for file in self.test_dir.rglob("*"):
                if file.is_file():
                    file.unlink()
            try:
                self.test_dir.rmdir()
            except OSError:
                pass
    
    def test_recipe_workflow(self):
        """Test complete recipe storage workflow."""
        # Create a complete recipe
        ingredients = [
            Ingredient(
                name="chicken breast",
                quantity=2.0,
                unit=QuantityUnit.POUND,
                original_text="2 lbs boneless chicken breast",
                category="meat"
            ),
            Ingredient(
                name="olive oil",
                quantity=2.0,
                unit=QuantityUnit.TABLESPOON,
                original_text="2 tbsp olive oil",
                category="oil"
            )
        ]
        
        recipe = Recipe(
            title="Grilled Chicken",
            url="https://example.com/grilled-chicken",
            description="Simple grilled chicken recipe",
            servings=4,
            prep_time="10 minutes",
            cook_time="20 minutes",
            ingredients=ingredients,
            instructions=[
                "Preheat grill to medium-high heat",
                "Season chicken with salt and pepper",
                "Grill for 6-7 minutes per side",
                "Let rest for 5 minutes"
            ]
        )
        
        # Save recipe
        save_result = self.storage.save(recipe, "grilled_chicken", "json")
        self.assertIsNotNone(save_result)
        
        # Load recipe
        load_result = self.storage.load(recipe, "grilled_chicken", "json", model_class=Recipe)
        self.assertIsNotNone(load_result)
        
        loaded_recipe = load_result["object"]
        self.assertEqual(loaded_recipe.title, recipe.title)
        self.assertEqual(len(loaded_recipe.ingredients), 2)
        self.assertEqual(loaded_recipe.ingredients[0].name, "chicken breast")
    
    def test_multiple_formats_same_object(self):
        """Test saving the same object in multiple formats."""
        ingredient = Ingredient(
            name="tomatoes",
            quantity=3.0,
            unit=QuantityUnit.PIECE,
            original_text="3 medium tomatoes"
        )
        
        # Save in different formats
        json_result = self.storage.save(ingredient, "json_format", "json")
        pickle_result = self.storage.save(ingredient, "pickle_format", "pickle")
        string_result = self.storage.save(ingredient, "string_format", "string")
        
        # All should succeed
        self.assertIsNotNone(json_result)
        self.assertIsNotNone(pickle_result)
        self.assertIsNotNone(string_result)
        
        # Load and verify all formats
        json_loaded = self.storage.load(ingredient, "json_format", "json", model_class=Ingredient)
        pickle_loaded = self.storage.load(ingredient, "pickle_format", "pickle")
        string_loaded = self.storage.load(ingredient, "string_format", "string", model_class=Ingredient)
        
        # All should contain the same ingredient data
        self.assertEqual(json_loaded["object"].name, ingredient.name)
        self.assertEqual(pickle_loaded["object"].name, ingredient.name)
        self.assertEqual(string_loaded["object"].name, ingredient.name)
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets."""
        import time

        # Create large dataset
        large_recipe_list = []
        for i in range(100):
            recipe = Recipe(
                title=f"Recipe {i}",
                url=f"https://example.com/recipe-{i}",
                ingredients=[
                    Ingredient(
                        name=f"ingredient_{i}",
                        quantity=float(i),
                        unit=QuantityUnit.CUP,
                        original_text=f"{i} cups ingredient_{i}"
                    )
                ],
                instructions=[f"Step {j}" for j in range(1, 6)]
            )
            large_recipe_list.append(recipe)
        
        # Test JSON performance
        start_time = time.time()
        json_result = self.storage.save("large_json_test", large_recipe_list, "large_json", "json")
        json_save_time = time.time() - start_time
        
        start_time = time.time()
        json_loaded = self.storage.load("large_json_test", "large_json", "json")
        json_load_time = time.time() - start_time
        
        # Test Pickle performance
        start_time = time.time()
        pickle_result = self.storage.save("large_pickle_test", large_recipe_list, "large_pickle", "pickle")
        pickle_save_time = time.time() - start_time
        
        start_time = time.time()
        pickle_loaded = self.storage.load("large_pickle_test", "large_pickle", "pickle")
        pickle_load_time = time.time() - start_time
        
        # Verify both completed successfully
        self.assertIsNotNone(json_result)
        self.assertIsNotNone(pickle_result)
        self.assertIsNotNone(json_loaded)
        self.assertIsNotNone(pickle_loaded)
        
        print(f"\nPerformance Results:")
        print(f"JSON  - Save: {json_save_time:.4f}s, Load: {json_load_time:.4f}s")
        print(f"Pickle - Save: {pickle_save_time:.4f}s, Load: {pickle_load_time:.4f}s")
        
        # Performance should be reasonable (less than 10 seconds each)
        self.assertLess(json_save_time, 10.0)
        self.assertLess(json_load_time, 10.0)
        self.assertLess(pickle_save_time, 10.0)
        self.assertLess(pickle_load_time, 10.0)


if __name__ == "__main__":
    # Setup test environment
    setup_logging(debug=True)
    logger = get_logger(__name__)
    
    logger.info("Starting StorageManager Test Suite")
    logger.info("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestStorageManager))
    test_suite.addTest(unittest.makeSuite(TestStorageManagerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("Test Suite Summary:")
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    
    if result.failures:
        logger.error("FAILURES:")
        for test, traceback in result.failures:
            logger.error(f"  {test}: {traceback}")
    
    if result.errors:
        logger.error("ERRORS:")
        for test, traceback in result.errors:
            logger.error(f"  {test}: {traceback}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)