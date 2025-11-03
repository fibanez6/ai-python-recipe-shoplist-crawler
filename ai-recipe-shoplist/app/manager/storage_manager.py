"""Content storage for saving and loading web content to/from disk."""

import hashlib
import json
import pickle
import sys
import time
from pathlib import Path
from typing import Any, Optional

import joblib

from ..config.logging_config import get_logger, log_function_call
from ..config.pydantic_config import STORAGE_SETTINGS

logger = get_logger(__name__)

#  Original / source content
SOURCE_ALIAS="source"
PROCESSED_ALIAS = "processed"

class StorageManager:
    """Manages saving and loading of web content to/from disk files."""

    def __init__(self, base_path: Path = STORAGE_SETTINGS.base_path):
        """
        Initialize the content storage.
        
        Args:
            tmp_folder: Base temporary folder for storage
        """
        self.name = "StorageManager"
        self.base_path = base_path
        self.enabled = STORAGE_SETTINGS.enabled
        
        # Create content folder if needed and saving is enabled
        if self.enabled:
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[{self.name}] Using storage directory at: {self.base_path}")
        else:
            logger.warning(f"[{self.name}] Storage is disabled")

    def _object_to_str(self, obj: Any) -> str:
        """Convert an object to a string representation for hashing."""
        if hasattr(obj, 'model_dump_json'):
            return obj.model_dump_json()
        elif hasattr(obj, 'json'):
            return obj.json()
        elif hasattr(obj, '__dict__'):
            return str(obj.__dict__)
        else:
            return str(obj)

    def _get_hash(self, key: str, alias: str) -> str:
        """Generate a hash for the key and alias to use as filename base."""
        return hashlib.md5(f"{alias}_{key}".encode()).hexdigest()
    
     # ===== JSON SERIALIZATION (Best for Pydantic models) =====

    def save_pydantic_as_json(self, obj: Any, filename: str) -> Path:
        """Save a Pydantic model as a JSON file."""
        file_path = self.base_path / f"{filename}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            # Use Pydantic's built-in JSON serialization
            if hasattr(obj, 'model_dump_json'):
                # Pydantic v2
                f.write(obj.model_dump_json(indent=2))
            elif hasattr(obj, 'json'):
                # Pydantic v1
                f.write(obj.json(indent=2))
            else:
                # Fallback for regular objects
                json.dump(obj.dict() if hasattr(obj, 'dict') else obj, f, indent=2, default=str)
                
        logger.debug(f"[{self.name}] Saved Pydantic object to JSON file: {file_path}")
        return file_path
    
    def load_pydantic_from_json(self, filename: str, model_class: type) -> Any:
        """
        Load a Pydantic model from JSON.
        
        Args:
            filename: Name of the file (without .json extension)
            model_class: The Pydantic model class (e.g., Recipe, Product)
        """
        file_path = self.base_path / f"{filename}.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create the Pydantic model from the loaded data
        obj = model_class(**data) if isinstance(data, dict) else model_class.parse_obj(data)
        print(f"✅ Loaded {model_class.__name__} from: {file_path}")
        return obj

    # ===== PICKLE SERIALIZATION (For complex Python objects) =====

    def save_with_pickle(self, obj: Any, filename: str) -> Path:
        """Save an object using pickle serialization."""
        file_path = self.base_path / f"{filename}.pkl"

        with open(file_path, 'wb') as f:
            pickle.dump(obj, f)
            
        logger.debug(f"[{self.name}] Saved object to pickle file: {file_path}")
        return file_path

    def load_with_pickle(self, filename: str) -> Any:
        """Load an object that was saved with pickle."""
        file_path = self.base_path / f"{filename}.pkl"
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            obj = pickle.load(f)
        
        print(f"✅ Loaded object with pickle from: {file_path}")
        return obj
    
    # ===== JOBLIB SERIALIZATION (Efficient for large objects) =====

    def save_with_joblib(self, obj: Any, filename: str) -> Path:
        """Save an object using joblib serialization."""
        file_path = self.base_path / f"{filename}.joblib"

        joblib.dump(obj, file_path)
        logger.debug(f"[{self.name}] Saved object to joblib file: {file_path}")
        return file_path

    def load_with_joblib(self, filename: str) -> Any:
        """Load an object that was saved with joblib."""
        file_path = self.base_path / f"{filename}.joblib"
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        obj = joblib.load(file_path)
        print(f"✅ Loaded object with joblib from: {file_path}")
        return obj
      
    # ===== CUSTOM JSON SERIALIZATION (For complex objects) =====
    
    def save_custom_json(self, obj: Any, filename: str, custom_encoder=None) -> Path:
        """
        Save objects with custom JSON encoding.
        Useful when you need custom serialization logic.
        """
        file_path = self.base_path / f"{filename}_custom.json"
        
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if custom_encoder:
                    return custom_encoder(obj)
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                if hasattr(obj, 'isoformat'):  # datetime objects
                    return obj.isoformat()
                return str(obj)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, cls=CustomEncoder, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved object with custom JSON to: {file_path}")
        return file_path

    def load_custom_json(self, filename: str, custom_decoder=None) -> Any:
        """Load objects with custom JSON decoding."""
        file_path = self.base_path / f"{filename}_custom.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if custom_decoder:
            data = custom_decoder(data)
        
        print(f"✅ Loaded object with custom JSON from: {file_path}")
        return data

    # ===== STRING/TEXT SERIALIZATION =====
    def save_as_string(self, data: str, filename: str, format: str = "txt") -> Path:
        """
        Save plain string/text data to a file.
        """
        file_path = self.base_path / f"{filename}.{format}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)
        
        print(f"✅ Saved string data to: {file_path}")
        return file_path

    def load_as_string(self, filename: str, format: str = "txt") -> str:
        """Load plain string/text data from a file."""
        file_path = self.base_path / f"{filename}.{format}"
            
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        
        print(f"✅ Loaded string data from: {file_path}")
        return data

    def save_object_as_string(self, obj: Any, filename: str) -> Path:
        """
        Convert any object to string representation and save it.
        Useful for debugging or simple text storage.
        """
        file_path = self.base_path / f"{filename}_str.txt"
        
        # Convert object to string
        if hasattr(obj, 'model_dump_json'):
            # Pydantic v2
            string_data = obj.model_dump_json(indent=2)
        elif hasattr(obj, 'json'):
            # Pydantic v1
            string_data = obj.json(indent=2)
        elif hasattr(obj, '__dict__'):
            string_data = json.dumps(obj.__dict__, indent=2, default=str)
        else:
            string_data = str(obj)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(string_data)
        
        print(f"✅ Saved object as string to: {file_path}")
        return file_path

    def load_string_as_json(self, filename: str, model_class: type = None) -> Any:
        """
        Load string data and attempt to parse as JSON.
        Optionally reconstruct as Pydantic model.
        """
        file_path = self.base_path / f"{filename}_str.txt"
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            string_data = f.read()
        
        try:
            # Try to parse as JSON
            json_data = json.loads(string_data)
            
            if model_class:
                # Reconstruct as Pydantic model
                obj = model_class(**json_data)
                print(f"✅ Loaded and reconstructed {model_class.__name__} from string: {file_path}")
                return obj
            else:
                print(f"✅ Loaded JSON data from string: {file_path}")
                return json_data
                
        except json.JSONDecodeError:
            # Return as plain string if not valid JSON
            print(f"✅ Loaded plain string data from: {file_path}")
            return string_data

    # ===== Metadata Management =====

    def _save_metadata(self, filename: str, file_path: Path, alias: str, obj_size: int, format: str) -> dict:
        """Save metadata dictionary to a JSON file."""
        metadata_path = self.base_path / f"{filename}_metadata.json"

        metadata = {
            "filename": filename,
            "alias": alias,
            "timestamp": time.time(),
            "file_path": str(file_path),
            "data_size": f"{obj_size} bytes ({obj_size/1024:.2f} KB)",
            "data_format": format
        }

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.debug(f"[{self.name}] Saved metadata to JSON file: {metadata_path}")
        return metadata

    def _load_metadata(self, filename: str) -> dict:
        """Load metadata dictionary from a JSON file."""
        metadata_path = self.base_path / f"{filename}_metadata.json"

        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        logger.debug(f"[{self.name}] Loaded metadata from JSON file: {metadata_path}")
        return metadata

    # ===== GENERIC SAVE/LOAD  =====

    # def save(self, key: str, obj: Any, alias: str = SOURCE_ALIAS, format: str = "json", **kwargs) -> dict[str, str]:
        
    def save(self, key: str, obj: Any, alias: str = SOURCE_ALIAS, format: str = "json", **kwargs) -> dict[str, str]:
        """
        Generic save method that dispatches to appropriate serialization format.
        
        Args:
            key: Unique Key for the content
            obj: Object to save
            alias: Alias for the content (e.g., 'source', 'processed')
            format: Serialization format ('json', 'pickle', 'joblib', 'custom_json', 'html', 'string')
            **kwargs: Additional arguments for specific methods (e.g., model_class, custom_encoder)

        Returns:
            dict with file path of saved data (empty if saving disabled)
        """
        if not self.enabled:
            return None

        obj_str = self._object_to_str(obj)
        obj_size = sys.getsizeof(obj_str)

        log_function_call("StorageManager.save", {
            "data_preview": obj_str[:20] + ("..." if len(obj_str) > 20 else ""),
            "data_type": type(obj).__name__,
            "alias": alias,
            "format": format,
            "path": str(self.base_path)
        })

        load_from = kwargs.get('data_from', None)
        if load_from == "local_disk":
            logger.debug(f"[{self.name}] Skipping save since data loaded from local disk")
            return None

        format = format.lower() 
        filename = self._get_hash(key, alias)
        
        try:
            # Dispatch to the appropriate save format
            if format == "json":
                file_path = self.save_pydantic_as_json(obj, filename)
            elif format == "pickle":
                file_path = self.save_with_pickle(obj, filename)
            elif format == "joblib":
                file_path = self.save_with_joblib(obj, filename)
            elif format == "custom_json":
                custom_encoder = kwargs.get('custom_encoder', None)
                file_path = self.save_custom_json(obj, filename, custom_encoder)
            elif format == "html":
                file_path = self.save_as_string(obj, filename, format="html")
            elif format == "string":
                if isinstance(obj, str):
                    file_path = self.save_as_string(obj, filename)
                else:
                    file_path = self.save_object_as_string(obj, filename)
            else:
                file_path = self.save_as_string(obj, filename)

            # Prepare metadata
            metadata = self._save_metadata(filename, file_path, alias, obj_size, format)
            logger.info(f"[{self.name}] Saved content to {file_path} and alias '{alias}'")
            return metadata
        except IOError as e:
            logger.warning(f"[{self.name}] Error saving content to disk for {filename}: {e}")
            return None

    def load(self, key: str, alias: str = SOURCE_ALIAS, format: str = None, **kwargs) -> Optional[dict]:
        """
        Generic load method that dispatches to appropriate deserialization format.
        
        Args:
            obj: Object to load
            alias: Alias for the content (e.g., 'source', 'processed')
            format: Serialization format used ('json', 'pickle', 'joblib', 'custom_json', 'html', 'string' or None to auto-detect)
            **kwargs: Additional arguments for specific methods (e.g., model_class, custom_decoder)
        
        Returns:
            The loaded object
        """
        if not self.enabled:
            return None

        log_function_call("StorageManager.load", {
            "storage_key": key,
            "alias": alias,
            "format": format,
            "path": str(self.base_path)
        })
        
        try:
            metadata = {}
            filename = self._get_hash(key, alias)

            # Determine format from metadata if not provided
            if not format:
                metadata = self._load_metadata(filename)
                format = metadata.get("data_format", "string")
            else:
                format = format.lower()

            # Dispatch to the appropriate load format
            if format == "json":
                model_class = kwargs.get('model_class')
                if not model_class:
                    raise ValueError("model_class is required for JSON deserialization")
                obj = self.load_pydantic_from_json(filename, model_class)
            elif format == "pickle":
                obj = self.load_with_pickle(filename)
            elif format == "joblib":
                obj = self.load_with_joblib(filename)
            elif format == "custom_json":
                custom_decoder = kwargs.get('custom_decoder', None)
                obj = self.load_custom_json(filename, custom_decoder)
            elif format == "html":
                obj = self.load_as_string(filename, format="html")
            elif format == "string":
                model_class = kwargs.get('model_class', None)
                if model_class:
                    obj = self.load_string_as_json(filename, model_class)
                else:
                    obj = self.load_as_string(filename)
            else:
               obj = self.load_as_string(filename)

            # Update metadata with loaded data info
            metadata["data_from"] = "local_disk"
            metadata["data"] = obj

            logger.info(f"[{self.name}] Storage hit for key {filename} - {format} data from disk (alias='{alias}')")
            return metadata
        except FileNotFoundError:
            logger.warning(f"[{self.name}] No content file found on disk for {filename} in path {self.base_path} (alias='{alias}')")
            return None
        except IOError as e:
            logger.warning(f"[{self.name}] Error reading content file for {filename} in path {self.base_path} (alias='{alias}'): {e}")
            return None
        except Exception as e:
            logger.warning(f"[{self.name}] Unexpected error loading content for {filename} in path {self.base_path} (alias='{alias}'): {e}")
            return None

    # ===== Clear Storage =====

    def clear(self) -> int:
        """
        Remove all files in the content folder.

        Returns:
            Number of files removed.
        """
        removed_files = 0

        if not self.base_path.exists():
            logger.info(f"[{self.name}] Content folder does not exist, nothing to clear.")
            return removed_files

        for content_file in self.base_path.iterdir():
            try:
                content_file.unlink()
                removed_files += 1
            except OSError as e:
                logger.warning(f"[{self.name}] Failed to remove file {content_file}: {e}")

        # Attempt to remove the folder if empty
        try:
            self.base_path.rmdir()
        except OSError:
            pass  # Folder not empty or cannot be removed

        logger.info(f"[{self.name}] Removed {removed_files} content files")
        return removed_files

    # ===== Storage Statistics =====

    def get_stats(self) -> dict[str, any]:
        """Get content storage statistics."""
        content_files_count = 0
        content_files_size = 0
        
        if self.base_path.exists():
            for content_file in self.base_path.iterdir():
                try:
                    content_files_count += 1
                    content_files_size += content_file.stat().st_size
                except OSError:
                    pass  # Skip files that can't be accessed
        
        return {
            "entries": content_files_count,
            "total_size": content_files_size,
            "folder": str(self.base_path) if self.base_path.exists() else "N/A",
            "saving_enabled": self.enable_saving,
            "loading_enabled": self.enable_loading
        }

# Global storage instance
_storage_instance = None

def get_storage_manager() -> StorageManager:
    """Get or create the global content storage instance."""
    global _storage_instance
    base_path = STORAGE_SETTINGS.base_path / "web_cache"

    if _storage_instance is None:
        _storage_instance = StorageManager(base_path)
    return _storage_instance