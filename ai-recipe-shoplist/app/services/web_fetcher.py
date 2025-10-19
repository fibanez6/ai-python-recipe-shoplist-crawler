"""Web content fetcher service for downloading recipe pages and other web content."""

import os
import time
from typing import Any, Dict

import httpx
from bs4 import BeautifulSoup

from ..config.logging_config import get_logger, log_api_request, log_function_call

logger = get_logger(__name__)


class WebFetcher:
    """Service for fetching web content with caching and error handling."""
    
    def __init__(self):
        self.timeout = int(os.getenv("FETCHER_TIMEOUT", "30"))
        self.max_content_size = int(os.getenv("FETCHER_MAX_SIZE", "10485760"))  # 10MB
        self.user_agent = os.getenv("FETCHER_USER_AGENT", 
            "Mozilla/5.0 (compatible; AI-Recipe-Crawler/1.0; +https://github.com/your-repo)")
        
        # Simple in-memory cache (use Redis in production)
        self._cache = {}
        self.cache_ttl = int(os.getenv("FETCHER_CACHE_TTL", "3600"))  # 1 hour
        
        logger.info(f"WebFetcher initialized - Timeout: {self.timeout}s, Max size: {self.max_content_size} bytes")
    
    async def fetch_url(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch content from a URL with caching and error handling.
        
        Args:
            url: URL to fetch
            use_cache: Whether to use cached content if available
            
        Returns:
            Dict containing:
                - content: HTML content
                - url: Final URL (after redirects)
                - status_code: HTTP status code
                - headers: Response headers
                - from_cache: Whether content was served from cache
        """
        log_function_call("WebFetcher.fetch_url", {"url": url, "use_cache": use_cache})
        
        # Check cache first
        if use_cache and url in self._cache:
            cache_entry = self._cache[url]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                logger.info(f"[WebFetcher] Serving cached content for {url}")
                cache_entry["from_cache"] = True
                return cache_entry
            else:
                # Cache expired
                del self._cache[url]
                logger.debug(f"Cache expired for {url}")
        
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
                    "size": content_length
                }
                
                # Cache the result
                if use_cache:
                    self._cache[url] = result.copy()
                    logger.debug(f"[WebFetcher] Cached content for {url} ({content_length} bytes)")
                
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
    
    async def fetch_recipe_content(self, url: str, clean_html: bool = True) -> Dict[str, Any]:
        """
        Fetch and optionally clean HTML content for recipe processing.
        
        Args:
            url: Recipe URL to fetch
            clean_html: Whether to clean HTML content for AI processing
            
        Returns:
            Dict containing fetched content and metadata
        """
        log_function_call("WebFetcher.fetch_recipe_content", {"url": url, "clean_html": clean_html})
        
        result = await self.fetch_url(url)
        
        if clean_html:
            result["cleaned_content"] = self._clean_html_for_ai(result["content"])
            logger.debug(f"[WebFetcher] Cleaned HTML content: {len(result['content'])} -> {len(result['cleaned_content'])} chars")

        return result
    
    def _clean_html_for_ai(self, html_content: str, max_length: int = 100000) -> str:
        """
        Clean HTML content for AI processing by removing unnecessary elements.
        
        Args:
            html_content: Raw HTML content
            max_length: Maximum length of cleaned content
            
        Returns:
            Cleaned HTML content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside", "svg", "link", "meta"]):
                element.decompose()
            
            # Remove comments
            from bs4 import Comment
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Remove empty elements
            for element in soup.find_all():
                if not element.get_text(strip=True) and not element.find_all():
                    element.decompose()
            
            # Get cleaned text
            cleaned = str(soup)
            
            # Remove empty lines and excessive whitespace
            lines = cleaned.split('\n')
            non_empty_lines = []
            for line in lines:
                stripped_line = line.strip()
                if stripped_line:  # Only keep non-empty lines
                    non_empty_lines.append(stripped_line)
            
            # Join lines back with single newlines
            cleaned = '\n'.join(non_empty_lines)
            
            # Truncate if too long
            if len(cleaned) > max_length:
                cleaned = cleaned[:max_length]
                logger.debug(f"[WebFetcher] Truncated HTML content to {max_length} characters")
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"[WebFetcher] Error cleaning HTML: {e}, returning truncated original")
            return html_content[:max_length]
    
    def clear_cache(self) -> None:
        """Clear the content cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info(f"[WebFetcher] Cleared fetcher cache ({cache_size} entries)")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "urls": list(self._cache.keys()),
            "total_size": sum(entry.get("size", 0) for entry in self._cache.values()),
            "ttl_seconds": self.cache_ttl
        }


# Global fetcher instance
_fetcher_instance = None

def get_web_fetcher() -> WebFetcher:
    """Get or create the global web fetcher instance."""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = WebFetcher()
    return _fetcher_instance