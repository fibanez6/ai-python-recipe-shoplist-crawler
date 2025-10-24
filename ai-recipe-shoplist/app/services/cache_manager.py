"""Cache management for web content with both memory and file-based caching."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

from ..config.logging_config import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Manages both memory and file-based caching for web content."""
    
    def __init__(self, tmp_folder: Path, cache_ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            tmp_folder: Temporary folder for file caching
            cache_ttl: Cache TTL in seconds (default: 3600 = 1 hour)
        """
        self.tmp_folder = tmp_folder
        self.cache_ttl = cache_ttl
        
        # Simple in-memory cache (use Redis in production)
        self._memory_cache = {}
        
        # Ensure tmp folder exists
        self.tmp_folder.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"[CacheManager] Initialized with folder: {self.tmp_folder}, TTL: {self.cache_ttl}s")
    
    def _get_cache_filename(self, url: str) -> Path:
        """Generate a cache filename based on URL hash."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.tmp_folder / f"{url_hash}.json"
    
    def get_from_memory_cache(self, url: str) -> Dict[str, Any] | None:
        """
        Get content from memory cache if available and not expired.
        
        Args:
            url: URL to get cached content for
            
        Returns:
            Cached content dict or None if not found/expired
        """
        if url not in self._memory_cache:
            return None
        
        cache_entry = self._memory_cache[url]
        if time.time() - cache_entry["timestamp"] < self.cache_ttl:
            logger.info(f"[CacheManager] Serving cached content from memory for {url}")
            cache_entry["from_cache"] = True
            cache_entry["from_file_cache"] = False
            return cache_entry
        else:
            # Cache expired
            del self._memory_cache[url]
            logger.debug(f"[CacheManager] Memory cache expired for {url}")
            return None
    
    def save_to_memory_cache(self, url: str, data: Dict[str, Any]) -> None:
        """
        Save content to memory cache.
        
        Args:
            url: URL of the content
            data: Content data to cache
        """
        self._memory_cache[url] = data.copy()
        logger.debug(f"[CacheManager] Saved content to memory cache for {url}")
    
    def get_from_file_cache(self, url: str) -> Dict[str, Any] | None:
        """
        Load content from file cache if available and not expired.
        
        Args:
            url: URL to get cached content for
            
        Returns:
            Cached content dict or None if not found/expired
        """
        cache_file = self._get_cache_filename(url)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            if time.time() - cache_data.get("timestamp", 0) > self.cache_ttl:
                logger.debug(f"[CacheManager] File cache expired for {url}, removing {cache_file}")
                cache_file.unlink(missing_ok=True)
                return None
            
            logger.info(f"[CacheManager] Serving content from file cache for {url}")
            cache_data["from_cache"] = True
            cache_data["from_file_cache"] = True
            return cache_data
            
        except (json.JSONDecodeError, KeyError, IOError) as e:
            logger.warning(f"[CacheManager] Error reading file cache for {url}: {e}")
            cache_file.unlink(missing_ok=True)  # Remove corrupted cache file
            return None
    
    def save_to_file_cache(self, url: str, data: Dict[str, Any]) -> None:
        """
        Save content to file cache.
        
        Args:
            url: URL of the content
            data: Content data to cache
        """
        cache_file = self._get_cache_filename(url)
        
        try:
            # Create a copy without from_cache flag for saving
            cache_data = data.copy()
            cache_data.pop("from_cache", None)
            cache_data.pop("from_file_cache", None)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.debug(f"[CacheManager] Saved content to file cache: {cache_file}")
            
        except (IOError, json.JSONEncodeError) as e:
            logger.warning(f"[CacheManager] Error saving to file cache for {url}: {e}")
    
    def get_cached_content(self, url: str, use_cache: bool = True) -> Dict[str, Any] | None:
        """
        Get cached content from memory or file cache.
        
        Args:
            url: URL to get cached content for
            use_cache: Whether to use cache
            
        Returns:
            Cached content dict or None if not found
        """
        if not use_cache:
            return None
        
        # Check memory cache first
        memory_result = self.get_from_memory_cache(url)
        if memory_result:
            return memory_result
        
        # Check file cache if memory cache miss
        file_result = self.get_from_file_cache(url)
        if file_result:
            # Also store in memory cache for faster subsequent access
            self.save_to_memory_cache(url, file_result.copy())
            return file_result
        
        return None
    
    def save_content(self, url: str, data: Dict[str, Any], use_cache: bool = True) -> None:
        """
        Save content to both memory and file cache.
        
        Args:
            url: URL of the content
            data: Content data to cache
            use_cache: Whether to use cache
        """
        if not use_cache:
            return
        
        self.save_to_memory_cache(url, data)
        self.save_to_file_cache(url, data)
        
        content_length = data.get("size", 0)
        logger.debug(f"[CacheManager] Cached content for {url} ({content_length} bytes)")
    
    def clear_cache(self, clear_file_cache: bool = True) -> Dict[str, int]:
        """
        Clear the cache.
        
        Args:
            clear_file_cache: Whether to also clear the file cache
            
        Returns:
            Dict with counts of cleared items
        """
        memory_cache_size = len(self._memory_cache)
        self._memory_cache.clear()
        
        file_cache_count = 0
        
        if clear_file_cache and self.tmp_folder.exists():
            # Clear JSON cache files
            for cache_file in self.tmp_folder.glob("*.json"):
                try:
                    cache_file.unlink()
                    file_cache_count += 1
                except OSError as e:
                    logger.warning(f"[CacheManager] Error removing cache file {cache_file}: {e}")
        
        logger.info(f"[CacheManager] Cleared cache (memory: {memory_cache_size}, files: {file_cache_count})")
        
        return {
            "memory_entries": memory_cache_size,
            "file_entries": file_cache_count
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        # Get file cache stats
        file_cache_count = 0
        file_cache_size = 0
        
        if self.tmp_folder.exists():
            for cache_file in self.tmp_folder.glob("*.json"):
                try:
                    file_cache_count += 1
                    file_cache_size += cache_file.stat().st_size
                except OSError:
                    pass  # Skip files that can't be accessed
        
        return {
            "memory_cache": {
                "entries": len(self._memory_cache),
                "urls": list(self._memory_cache.keys()),
                "total_size": sum(entry.get("size", 0) for entry in self._memory_cache.values())
            },
            "file_cache": {
                "entries": file_cache_count,
                "total_size": file_cache_size,
                "folder": str(self.tmp_folder)
            },
            "ttl_seconds": self.cache_ttl
        }