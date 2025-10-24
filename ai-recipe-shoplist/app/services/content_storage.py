"""Content storage for saving and loading web content to/from disk."""

import hashlib
import os
import time
from pathlib import Path
from typing import Dict

from ..config.logging_config import get_logger

logger = get_logger(__name__)


class ContentStorage:
    """Manages saving and loading of web content to/from disk files."""
    
    def __init__(self, tmp_folder: Path, enable_saving: bool = False, enable_loading: bool = False):
        """
        Initialize the content storage.
        
        Args:
            tmp_folder: Base temporary folder for storage
            enable_saving: Whether content saving is enabled
            enable_loading: Whether content loading is enabled
        """
        self.tmp_folder = tmp_folder
        self.enable_saving = enable_saving
        self.enable_loading = enable_loading
        
        # Content folder inside tmp folder
        self.content_folder = self.tmp_folder / "content"
        
        # Create content folder if needed and saving is enabled
        if self.enable_saving:
            self.content_folder.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"[ContentStorage] Initialized - Saving: {self.enable_saving}, Loading: {self.enable_loading}")
        logger.debug(f"[ContentStorage] Content folder: {self.content_folder}")
    
    def _get_url_hash(self, url: str) -> str:
        """Generate a hash for the URL to use as filename base."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def save_content(self, url: str, original_content: str, cleaned_content: str = None) -> Dict[str, str]:
        """
        Save both original and cleaned content to separate files on disk.
        
        Args:
            url: URL of the content
            original_content: Original HTML content
            cleaned_content: Cleaned content (optional)
            
        Returns:
            Dict with file paths of saved content (empty if saving disabled)
        """
        if not self.enable_saving:
            logger.debug(f"[ContentStorage] Content saving disabled for {url}")
            return {}
        
        url_hash = self._get_url_hash(url)
        
        # Ensure content folder exists
        self.content_folder.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        try:
            # Save original content
            original_file = self.content_folder / f"{url_hash}_original.html"
            with open(original_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            saved_files["original_file"] = str(original_file)
            logger.debug(f"[ContentStorage] Saved original content to: {original_file}")
            
            # Save cleaned content if provided
            if cleaned_content:
                cleaned_file = self.content_folder / f"{url_hash}_cleaned.html"
                with open(cleaned_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                saved_files["cleaned_file"] = str(cleaned_file)
                logger.debug(f"[ContentStorage] Saved cleaned content to: {cleaned_file}")
            
            # Save URL mapping for reference
            url_mapping_file = self.content_folder / f"{url_hash}_url.txt"
            with open(url_mapping_file, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write(f"Hash: {url_hash}\n")
                f.write(f"Timestamp: {time.time()}\n")
                f.write(f"Original file: {saved_files.get('original_file', 'N/A')}\n")
                f.write(f"Cleaned file: {saved_files.get('cleaned_file', 'N/A')}\n")
            saved_files["url_mapping_file"] = str(url_mapping_file)
            
            logger.info(f"[ContentStorage] Saved content files for {url} (hash: {url_hash})")
            
        except IOError as e:
            logger.warning(f"[ContentStorage] Error saving content to disk for {url}: {e}")
        
        return saved_files
    
    def load_content(self, url: str) -> Dict[str, str]:
        """
        Load both original and cleaned content from disk if available.
        
        Args:
            url: URL of the content
            
        Returns:
            Dict with content loaded from disk (empty if not found or loading disabled)
        """
        if not self.enable_loading:
            logger.debug(f"[ContentStorage] Content loading disabled for {url}")
            return {}
        
        if not self.content_folder.exists():
            return {}
        
        url_hash = self._get_url_hash(url)
        loaded_content = {}
        
        try:
            # Load original content
            original_file = self.content_folder / f"{url_hash}_original.html"
            if original_file.exists():
                with open(original_file, 'r', encoding='utf-8') as f:
                    loaded_content["original_content"] = f.read()
                logger.debug(f"[ContentStorage] Loaded original content from: {original_file}")
            
            # Load cleaned content
            cleaned_file = self.content_folder / f"{url_hash}_cleaned.html"
            if cleaned_file.exists():
                with open(cleaned_file, 'r', encoding='utf-8') as f:
                    loaded_content["cleaned_content"] = f.read()
                logger.debug(f"[ContentStorage] Loaded cleaned content from: {cleaned_file}")
            
            # Load URL mapping
            url_mapping_file = self.content_folder / f"{url_hash}_url.txt"
            if url_mapping_file.exists():
                with open(url_mapping_file, 'r', encoding='utf-8') as f:
                    loaded_content["url_mapping"] = f.read()
            
            if loaded_content:
                logger.info(f"[ContentStorage] Loaded content from disk for {url} (hash: {url_hash})")
            
        except IOError as e:
            logger.warning(f"[ContentStorage] Error loading content from disk for {url}: {e}")
        
        return loaded_content
    
    def has_cleaned_content(self, url: str) -> bool:
        """
        Check if cleaned content exists on disk for the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if cleaned content file exists, False otherwise
        """
        if not self.enable_loading or not self.content_folder.exists():
            return False
        
        url_hash = self._get_url_hash(url)
        cleaned_file = self.content_folder / f"{url_hash}_cleaned.html"
        return cleaned_file.exists()
    
    def clear_content_files(self) -> int:
        """
        Clear all saved content files.
        
        Returns:
            Number of files cleared
        """
        content_files_count = 0
        
        if self.content_folder.exists():
            for content_file in self.content_folder.iterdir():
                try:
                    content_file.unlink()
                    content_files_count += 1
                except OSError as e:
                    logger.warning(f"[ContentStorage] Error removing content file {content_file}: {e}")
            
            # Remove empty content folder
            try:
                self.content_folder.rmdir()
            except OSError:
                pass  # Folder might not be empty
        
        logger.info(f"[ContentStorage] Cleared {content_files_count} content files")
        return content_files_count
    
    def get_content_stats(self) -> Dict[str, any]:
        """Get content storage statistics."""
        content_files_count = 0
        content_files_size = 0
        
        if self.content_folder.exists():
            for content_file in self.content_folder.iterdir():
                try:
                    content_files_count += 1
                    content_files_size += content_file.stat().st_size
                except OSError:
                    pass  # Skip files that can't be accessed
        
        return {
            "entries": content_files_count,
            "total_size": content_files_size,
            "folder": str(self.content_folder) if self.content_folder.exists() else "N/A",
            "saving_enabled": self.enable_saving,
            "loading_enabled": self.enable_loading
        }
    
    def update_config(self, enable_saving: bool = None, enable_loading: bool = None) -> None:
        """
        Update the content storage configuration.
        
        Args:
            enable_saving: New saving enabled state (None = no change)
            enable_loading: New loading enabled state (None = no change)
        """
        if enable_saving is not None:
            self.enable_saving = enable_saving
            logger.debug(f"[ContentStorage] Content saving updated to: {self.enable_saving}")
        
        if enable_loading is not None:
            self.enable_loading = enable_loading
            logger.debug(f"[ContentStorage] Content loading updated to: {self.enable_loading}")
        
        # Create content folder if saving is enabled
        if self.enable_saving:
            self.content_folder.mkdir(parents=True, exist_ok=True)