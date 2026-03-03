"""Storage module for PyShort - in-memory persistence layer."""

from typing import Dict, Optional
import json
from pathlib import Path

from pyshort.model import URL


class Storage:
    """In-memory storage for URLs with optional file persistence."""
    
    def __init__(self, storage_path: str | None = None):
        """
        Initialize the storage.
        
        Args:
            storage_path: Optional path to a JSON file for persistence
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.urls: Dict[str, URL] = {}
        self._load_from_file()
    
    def save(self, url: URL) -> None:
        """
        Save a URL object.
        
        Args:
            url: The URL object to save
        """
        self.urls[url.short_code] = url
        self._save_to_file()
    
    def get(self, short_code: str) -> Optional[URL]:
        """
        Retrieve a URL object by short code.
        
        Args:
            short_code: The short code to look up
            
        Returns:
            The URL object if found, None otherwise
        """
        return self.urls.get(short_code)
    
    def delete(self, short_code: str) -> bool:
        """
        Delete a URL by short code.
        
        Args:
            short_code: The short code to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        if short_code in self.urls:
            del self.urls[short_code]
            self._save_to_file()
            return True
        return False
    
    def exists(self, short_code: str) -> bool:
        """
        Check if a short code exists.
        
        Args:
            short_code: The short code to check
            
        Returns:
            True if the short code exists, False otherwise
        """
        return short_code in self.urls
    
    def get_all_urls(self) -> Dict[str, URL]:
        """
        Get all stored URLs.
        
        Returns:
            Dictionary mapping short codes to URL objects
        """
        return self.urls.copy()
    
    def get_short_codes(self) -> list[str]:
        """
        Get all short codes.
        
        Returns:
            List of all short codes
        """
        return list(self.urls.keys())
    
    def clear(self) -> None:
        """Clear all stored URLs."""
        self.urls.clear()
        self._save_to_file()
    
    def count(self) -> int:
        """
        Get the total number of stored URLs.
        
        Returns:
            The count of stored URLs
        """
        return len(self.urls)
    
    def _save_to_file(self) -> None:
        """Save storage to file if storage_path is configured."""
        if not self.storage_path:
            return
        
        try:
            data = {
                short_code: url.to_dict()
                for short_code, url in self.urls.items()
            }
            
            # Ensure parent directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Silently fail on storage errors to not disrupt main functionality
            pass
    
    def _load_from_file(self) -> None:
        """Load storage from file if storage_path exists."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.urls = {
                short_code: URL.from_dict(url_data)
                for short_code, url_data in data.items()
            }
        except Exception:
            # Start fresh if loading fails
            self.urls.clear()