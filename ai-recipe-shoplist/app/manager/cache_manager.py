"""Cache management for web content with both memory and file-based caching."""

import hashlib
import sys
import time
from typing import Any, Optional

from cachetools import TTLCache

from ..config.logging_config import get_logger, log_function_call
from ..config.pydantic_config import CACHE_SETTINGS
from ..utils.str_helpers import object_to_str

logger = get_logger(__name__)

#  Original / source content
SOURCE_ALIAS="source"
PROCESSED_ALIAS = "processed"

class CacheManager:
    """Manages caching for web content using (in-memory TTL cache) only."""

    def __init__(self, ttl: int = CACHE_SETTINGS.ttl):
        self.name = "CacheManager"
        self.enabled = CACHE_SETTINGS.enabled
        self.ttl = ttl
        self.max_size = CACHE_SETTINGS.max_size
        self.cache = TTLCache(maxsize=self.max_size, ttl=self.ttl)

        if self.enabled:
            logger.info(f"[{self.name}] Using TTLCache (maxsize={self.max_size}, ttl={self.ttl}s)")
        else:
            logger.warning(f"[{self.name}] Caching is disabled")
        
    def _get_hash(self, key: str, alias: str) -> str:
        """Generate a hash for the key and alias to use as cache_key."""
        return hashlib.md5(f"{alias}_{key}".encode()).hexdigest()
    
    def save(self, key: str, obj: any, alias: str = SOURCE_ALIAS, format: str = "json", **kwargs) -> dict:
        """
        Save content to in-memory cache.
        """
        if not self.enabled:
            return None
        
        obj_str = object_to_str(obj)
        obj_size = sys.getsizeof(obj_str)
        
        log_function_call("CacheManager.save", {
            "cache_key": key,
            "alias": alias,
            "data_preview": obj_str[:20] + ("..." if len(obj_str) > 20 else ""),
            "format": format
        })

        load_from = kwargs.get('data_from', None)
        if load_from == "local_cache":
            logger.debug(f"[{self.name}] Skipping save since data loaded from local cache")
            return None

        format = format.lower()

        cache_key = self._get_hash(key, alias)
        cache_entry = {
            "cache_key": cache_key,
            "alias": alias,
            "timestamp": time.time(),
            "data_size": f"{obj_size} bytes ({obj_size/1024:.2f} KB)",
            "data_format": format,
            "data": obj
        }

        self.cache[cache_key] = cache_entry

        logger.debug(f"[{self.name}] Saved obj to cache for {cache_key} and alias '{alias}'")

        return cache_entry

    def load(self, key: str, alias: str = SOURCE_ALIAS) -> Optional[dict]:
        """
        Retrieve content from in-memory cache if available and not expired.
        """
        if not self.enabled:
            return None

        log_function_call("CacheManager.load", {
            "cache_key": key,
            "alias": alias
        })

        cache_key = self._get_hash(key, alias)

        # Check if the cache entry exists
        cache_entry = self.cache.get(cache_key)
        if cache_entry is not None:
            cache_entry["data_from"] = "local_cache"
            logger.info(f"[{self.name}] Cache hit for key: {cache_key} (alias='{alias}')")
            return cache_entry

        logger.debug(f"[{self.name}] Cache miss for key: {cache_key} (alias='{alias}')")
        return None

    def clear(self) -> dict[str, int]:
        """
        Clear all in-memory cache entries.
        """
        if not self.enabled:
            return {"cachetools_cleared": 0}

        cleared = len(self.cache)
        self.cache.clear()
        logger.info(f"[{self.name}] Cleared all cache entries.")
        return {"cachetools_cleared": cleared}

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics (only)."""

        if not self.enabled:
            return {
                "enabled": False,
                "entries": 0,
                "keys": [],
                "ttl_seconds": self.ttl,
                "max_size": self.max_size
            }
        
        return {
            "enabled": True,
            "entries": len(self.cache),
            "keys": list(self.cache.keys()),
            "ttl_seconds": self.ttl,
            "max_size": self.max_size
        }

# Global cache instance
_cache_instance = None

def get_cache_manager(ttl: Optional[int] = None) -> CacheManager:
    """Get or create the global cache manager instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager(ttl=ttl) if ttl is not None else CacheManager()
    return _cache_instance
