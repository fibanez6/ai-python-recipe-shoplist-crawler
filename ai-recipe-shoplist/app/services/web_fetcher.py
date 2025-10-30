"""Web content fetcher service for downloading recipe pages and other web content."""

import time
from pathlib import Path
from typing import Any, Dict

import httpx

from ..config.logging_config import get_logger, log_api_request, log_function_call
from ..config.pydantic_config import FETCHER_SETTINGS
from ..utils.html_helpers import clean_html_for_ai
from .cache_manager import CacheManager
from .content_storage import WebContentStorage

logger = get_logger(__name__)


class WebFetcher:
    """Service for fetching web content with caching and error handling."""
    
    def __init__(self):
        self.timeout = FETCHER_SETTINGS.timeout
        self.max_content_size = FETCHER_SETTINGS.max_size
        self.user_agent = FETCHER_SETTINGS.user_agent

        # Cache TTL configuration
        cache_ttl = FETCHER_SETTINGS.cache_ttl

        # Setup tmp folder for file-based caching
        self.tmp_folder = Path(FETCHER_SETTINGS.tmp_folder)

        # Initialize cache manager and content storage
        self.cache_manager = CacheManager(cache_ttl)
        self.content_storage = WebContentStorage(self.tmp_folder)
        
        logger.info(f"WebFetcher initialized - Timeout: {self.timeout}s, Max size: {self.max_content_size} bytes")
        logger.info(f"WebFetcher tmp folder: {self.tmp_folder}")
    
    async def fetch_url(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch content from a URL with optional caching and robust error handling.

        Args:
            url (str): The URL to fetch.
            use_cache (bool): Whether to use cached content if available.

        Returns:
            Dict[str, Any]: Dictionary with:
            - content (str): HTML content.
            - url (str): Final URL after redirects.
            - status_code (int): HTTP status code.
            - headers (dict): Response headers.
            - timestamp (float): Fetch timestamp.
            - from_cache (bool): True if served from in-memory cache.
            - from_file_cache (bool): True if served from file cache.
            - size (int): Size of the content in bytes.
        """
        log_function_call("WebFetcher.fetch_url", {"url": url, "use_cache": use_cache})
        
        # Check cache using cache manager
        cached_result = self.cache_manager.get_cached_content(url, use_cache)
        if cached_result:
            return cached_result
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={"User-Agent": self.user_agent}
            ) as client:

                logger.info(f"[WebFetcher] Fetching URL: {url}")
                response = await client.get(url)
                response.raise_for_status()
                
                # Check content size
                content_length = len(response.content)
                if content_length > self.max_content_size:
                    raise ValueError(f"[WebFetcher] Content too large: {content_length} bytes (max: {self.max_content_size})")
                
                duration = time.time() - start_time
                
                # Log successful request
                log_api_request("WebFetcher", url, content_length, duration, True)
                
                result = {
                    "content": response.text,
                    "url": str(response.url),  # Final URL after redirects
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "timestamp": time.time(),
                    "from_cache": False,
                    "from_file_cache": False,
                    "size": content_length
                }
                
                # Cache the result using cache manager
                self.cache_manager.save_html_content(url, result, use_cache)
                
                logger.info(f"[WebFetcher] Successfully fetched {url} - {content_length} bytes in {duration:.2f}s")
                return result
              
        except httpx.TimeoutException:
            duration = time.time() - start_time
            log_api_request("WebFetcher", url, 0, duration, False)
            logger.error(f"[WebFetcher] Timeout fetching {url} after {duration:.2f}s")
            raise
        except httpx.HTTPStatusError as e:
            duration = time.time() - start_time
            log_api_request("WebFetcher", url, 0, duration, False)
            logger.error(f"[WebFetcher] HTTP error fetching {url}: {e.response.status_code}")
            raise
        except Exception as e:
            duration = time.time() - start_time
            log_api_request("WebFetcher", url, 0, duration, False)
            logger.error(f"[WebFetcher] Error fetching {url}: {e}")
            raise
    
    async def fetch_html_content(self, url: str, clean_html: bool = True) -> Dict[str, Any]:
        """
        Fetch HTML content from a URL, optionally cleaning it for AI processing.

        Args:
            url (str): The URL to fetch HTML content from.
            clean_html (bool): Whether to clean the HTML content for AI use.

        Returns:
            Dict[str, Any]: Dictionary with:
            - content (str): Raw HTML content.
            - cleaned_content (str): Cleaned HTML content (if requested).
            - loaded_from_disk (bool): True if loaded from disk cache.
            - saved_files (dict, optional): Paths to saved files if content was saved.
        """

        log_function_call("WebFetcher.fetch_html_content", {
            "url": url, 
            "clean_html": clean_html
        })
        
        # Load from storage
        content = self.content_storage.load_html_content(url)
        if content:
            logger.info(f"[WebFetcher] Using content from disk for {url}")
        
        # Fetch from web if not loaded from disk
        if "content" not in content:
            result = await self.fetch_url(url)
            content["content"] = result["content"]
            content["cleaned_content"] = result.get("cleaned_content", None)

        # Clean HTML if requested
        if clean_html and "cleaned_content" not in content:
            content["cleaned_content"] = clean_html_for_ai(content["content"])
            logger.debug(f"[WebFetcher] Generated cleaned HTML content: {len(content['content'])} -> {len(content['cleaned_content'])} chars")

        saved_files = self.content_storage.save_html_content(url, content)
        if saved_files:
            content["saved_files"] = saved_files

        return content


# Global fetcher instance
_fetcher_instance = None

def get_web_fetcher() -> WebFetcher:
    """Get or create the global web fetcher instance."""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = WebFetcher()
    return _fetcher_instance