# 💾 Storage System

The application features a sophisticated async storage system designed for high performance and flexibility:

## Storage Components

- **`BlobManager`**: Async blob storage supporting multiple serialization formats (JSON, Pickle, Joblib)
- **`CacheManager`**: High-performance memory caching with TTL and size limits
- **`StorageManager`**: Unified interface combining memory and disk storage operations

## Supported Formats

- **JSON**: Human-readable, ideal for Pydantic models and configuration data
- **Pickle**: Fast binary serialization for complex Python objects
- **Joblib**: Optimized for large scientific data (NumPy arrays, ML models)
- **Custom JSON**: Advanced JSON with custom encoders/decoders
- **String/Text**: Plain text storage for debugging and simple data

## Key Features

- **Fully Async**: All storage operations use `aiofiles` and `asyncio.to_thread()` for non-blocking I/O
- **Type Safety**: Pydantic model serialization with automatic type validation
- **Metadata Tracking**: Automatic metadata generation with timestamps, sizes, and formats
- **Error Handling**: Robust error handling with detailed logging
- **Cache Integration**: Seamless integration between memory cache and disk storage

## Usage Examples

### Basic Usage

```python
from app.storage.blob_manager import BlobManager
from app.models import Recipe

# Initialize storage
storage = BlobManager()

# Save Pydantic model as JSON
recipe = Recipe(title="Pasta", ingredients=[...])
await storage.save("recipe_123", recipe, format="json")

# Load with type reconstruction
loaded = await storage.load("recipe_123", format="json", model_class=Recipe)
```

### Advanced Usage

```python
# Save complex objects with Pickle
data = {"arrays": np.array([1,2,3]), "model": trained_model}
await storage.save("ml_data", data, format="pickle")

# Save large scientific data with Joblib
await storage.save("large_dataset", numpy_array, format="joblib")

# Custom JSON with encoder
def custom_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

await storage.save("custom_data", complex_obj, format="custom_json", 
                  custom_encoder=custom_encoder)
```

## Storage Architecture

### BlobManager

The `BlobManager` is the core component for persistent storage:

```python
# Multiple serialization formats
await storage.save_pydantic_as_json(recipe, "recipe_data")
await storage.save_with_pickle(complex_object, "object_data") 
await storage.save_with_joblib(large_array, "array_data")
await storage.save_as_string(text_content, "text_data")

# Automatic format detection on load
data = await storage.load("recipe_data")  # Auto-detects JSON format
```

### CacheManager

High-performance memory caching with configurable TTL:

```python
from app.storage.cache_manager import CacheManager

cache = CacheManager(max_size=1000, default_ttl=3600)

# Set with custom TTL
await cache.set("key", value, ttl=7200)

# Get with fallback
value = await cache.get("key", default="fallback_value")

# Batch operations
await cache.set_many({"key1": "value1", "key2": "value2"})
values = await cache.get_many(["key1", "key2"])
```

### StorageManager

Unified interface combining memory and disk storage:

```python
from app.storage.storage_manager import StorageManager

storage = StorageManager()

# Transparent caching - checks cache first, then disk
data = await storage.get("recipe_123")

# Save to both cache and disk
await storage.set("recipe_123", recipe_data)

# Cache-only operations
await storage.cache_set("temp_data", value, ttl=300)
```

## Configuration

Storage system configuration in `.env`:

```env
# =================================================================
# STORAGE CONFIGURATION
# =================================================================
BLOB_STORAGE_ENABLED=true            # Enable/disable blob storage
BLOB_STORAGE_BASE_PATH=tmp/storage   # Base path for blob storage
CACHE_ENABLED=true                   # Enable/disable memory caching
CACHE_MAX_SIZE=100                   # Maximum cache entries
CACHE_DEFAULT_TTL=3600              # Default cache TTL in seconds
```

## Performance Considerations

### Format Selection Guidelines

- **JSON**: Use for configuration data, small objects, human-readable storage
- **Pickle**: Use for complex Python objects, faster than JSON for large objects
- **Joblib**: Use for NumPy arrays, ML models, scientific data (most efficient)
- **Custom JSON**: Use when you need JSON with special serialization logic

### Async Best Practices

```python
# ✅ Good - Proper async usage
async def process_recipes(recipes):
    storage = BlobManager()
    tasks = []
    
    for recipe in recipes:
        task = storage.save(f"recipe_{recipe.id}", recipe, format="json")
        tasks.append(task)
    
    # Process all saves concurrently
    await asyncio.gather(*tasks)

# ❌ Bad - Blocking the event loop
def process_recipes_sync(recipes):
    for recipe in recipes:
        # This would block if not properly awaited
        storage.save(f"recipe_{recipe.id}", recipe, format="json")
```

### Memory Management

```python
# Use appropriate cache sizes
cache = CacheManager(
    max_size=1000,      # Adjust based on available memory
    default_ttl=3600    # Adjust based on data freshness needs
)

# Clean up when needed
await cache.clear()
await storage.clear()  # Removes all files
```

## Error Handling

The storage system includes comprehensive error handling:

```python
try:
    data = await storage.load("missing_key")
except FileNotFoundError:
    print("File not found - key doesn't exist")
except json.JSONDecodeError:
    print("Invalid JSON format")
except Exception as e:
    print(f"Unexpected error: {e}")

# Safe loading with defaults
data = await storage.load("key", format="json") or default_data
```

## Testing

### Unit Testing Storage Operations

```python
import pytest
import tempfile
from pathlib import Path
from app.storage.blob_manager import BlobManager

@pytest.mark.asyncio
async def test_json_storage():
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = BlobManager(base_path=Path(temp_dir))
        
        test_data = {"test": "data", "number": 42}
        
        # Test save
        metadata = await storage.save("test_key", test_data, format="json")
        assert metadata is not None
        
        # Test load
        loaded = await storage.load("test_key", format="json")
        assert loaded["data"] == test_data

@pytest.mark.asyncio 
async def test_cache_operations():
    cache = CacheManager(max_size=10)
    
    await cache.set("key1", "value1")
    value = await cache.get("key1")
    assert value == "value1"
    
    # Test TTL
    await cache.set("key2", "value2", ttl=1)
    await asyncio.sleep(2)
    value = await cache.get("key2")
    assert value is None  # Should be expired
```

## Migration and Compatibility

When upgrading storage formats or changing serialization:

```python
# Migration example
async def migrate_storage_format():
    storage = BlobManager()
    
    # Load old format
    old_data = await storage.load("data_key", format="pickle")
    
    if old_data:
        # Convert and save in new format
        await storage.save("data_key", old_data["data"], format="json")
        
        # Optionally remove old format file
        old_file = storage.base_path / "old_format_file.pkl"
        if old_file.exists():
            old_file.unlink()
```

## Troubleshooting

### Common Issues

**Storage directory not created**
- Ensure write permissions for `BLOB_STORAGE_BASE_PATH`
- Check disk space availability

**Serialization errors**
- Verify object compatibility with chosen format
- Use Pickle for complex objects that JSON can't handle
- Check for circular references in objects

**Performance issues**
- Monitor storage directory size
- Implement cleanup policies for old data
- Use appropriate format for data size (Joblib for large arrays)

**Memory cache issues**
- Increase `CACHE_MAX_SIZE` if cache misses are high
- Reduce `CACHE_DEFAULT_TTL` if memory usage is high
- Monitor cache hit rates and adjust accordingly

### Debugging

Enable debug logging to troubleshoot storage issues:

```env
LOG_LEVEL=DEBUG
LOG_DEBUG_ENABLED=true
```

Check storage statistics:

```python
# Get storage statistics
stats = await storage.get_stats()
print(f"Storage entries: {stats['entries']}")
print(f"Total size: {stats['total_size']} bytes")
print(f"Storage path: {stats['folder']}")

# Get cache statistics  
cache_stats = await cache.get_stats()
print(f"Cache entries: {cache_stats['entries']}")
print(f"Hit rate: {cache_stats['hit_rate']:.2%}")
```

---

The storage system is designed to be both powerful and easy to use, providing the flexibility needed for various data storage scenarios while maintaining high performance through async operations and intelligent caching.