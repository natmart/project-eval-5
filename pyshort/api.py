"""Main API facade for PyShort URL shortener service."""

from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from pyshort.validator import URLValidator
from pyshort.generator import ShortCodeGenerator
from pyshort.storage import Storage
from pyshort.stats import Stats
from pyshort.model import URL


class URLShortener:
    """Main API facade for the URL shortener service."""
    
    def __init__(
        self,
        storage_path: str | None = None,
        stats_path: str | None = None,
        code_length: int = 6
    ):
        """
        Initialize the URL Shortener service.
        
        Args:
            storage_path: Optional path to a JSON file for persistence of URLs
            stats_path: Optional path to a JSON file for persistence of statistics
            code_length: Length of generated short codes
        """
        self.validator = URLValidator()
        self.generator = ShortCodeGenerator(default_length=code_length)
        self.storage = Storage(storage_path=storage_path)
        self.stats = Stats(storage_path=stats_path)
        
        # Load existing codes into generator to avoid collisions
        existing_codes = self.storage.get_short_codes()
        self.generator.load_existing_codes(existing_codes)
    
    def shorten(self, url: str, custom_code: str | None = None) -> str:
        """
        Shorten a URL.
        
        Args:
            url: The original URL to shorten
            custom_code: Optional custom short code to use
            
        Returns:
            The short code for the shortened URL
            
        Raises:
            ValueError: If the URL is invalid or the custom code is invalid/already in use
        """
        # Validate the URL
        if not self.validator.validate(url):
            raise ValueError(f"Invalid URL: {url}")
        
        # Determine the short code to use
        if custom_code:
            # Use custom code
            if not self.validator.validate_short_code(custom_code):
                raise ValueError(f"Invalid short code: {custom_code}")
            if self.storage.exists(custom_code):
                raise ValueError(f"Short code already in use: {custom_code}")
            short_code = custom_code
        else:
            # Generate a new unique short code
            short_code = self.generator.generate()
        
        # Create and save the URL object
        url_obj = URL(
            short_code=short_code,
            original_url=url,
            custom_code=custom_code is not None
        )
        self.storage.save(url_obj)
        
        return short_code
    
    def resolve(self, short_code: str) -> Optional[str]:
        """
        Resolve a short code to the original URL.
        
        Args:
            short_code: The short code to resolve
            
        Returns:
            The original URL if found, None otherwise
        """
        url_obj = self.storage.get(short_code)
        
        if url_obj is None:
            return None
        
        # Record the access
        self.stats.record_access(short_code)
        
        # Update the URL object's access tracking
        url_obj.access_count += 1
        url_obj.last_accessed_at = datetime.utcnow()
        self.storage.save(url_obj)
        
        return url_obj.original_url
    
    def get_stats(self, short_code: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a short code.
        
        Args:
            short_code: The short code to get statistics for
            
        Returns:
            Dictionary containing statistics:
            - short_code: The short code
            - original_url: The original URL
            - created_at: ISO format timestamp
            - access_count: Total number of accesses
            - first_accessed_at: ISO format timestamp of first access (or None)
            - last_accessed_at: ISO format timestamp of last access (or None)
            - recent_accesses: List of recent access timestamps
            None if the short code doesn't exist
        """
        url_obj = self.storage.get(short_code)
        
        if url_obj is None:
            return None
        
        stats_data = self.stats.get_stats(short_code) or {
            "access_count": 0,
            "first_accessed_at": None,
            "last_accessed_at": None,
        }
        
        return {
            "short_code": short_code,
            "original_url": url_obj.original_url,
            "created_at": url_obj.created_at.isoformat(),
            "access_count": stats_data.get("access_count", 0),
            "first_accessed_at": stats_data.get("first_accessed_at"),
            "last_accessed_at": stats_data.get("last_accessed_at"),
            "recent_accesses": self.stats.get_recent_accesses(short_code, limit=10),
        }
    
    def delete(self, short_code: str) -> bool:
        """
        Delete a shortened URL.
        
        Args:
            short_code: The short code to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        if not self.storage.exists(short_code):
            return False
        
        # Delete from storage and stats
        self.storage.delete(short_code)
        self.stats.delete_stats(short_code)
        
        # Unregister from generator
        self.generator.unregister_code(short_code)
        
        return True
    
    def exists(self, short_code: str) -> bool:
        """
        Check if a short code exists.
        
        Args:
            short_code: The short code to check
            
        Returns:
            True if the short code exists, False otherwise
        """
        return self.storage.exists(short_code)
    
    def get_url_info(self, short_code: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a short code without recording an access.
        
        Args:
            short_code: The short code to get info for
            
        Returns:
            Dictionary containing URL information:
            - short_code: The short code
            - original_url: The original URL
            - created_at: ISO format timestamp
            - custom_code: Whether the code was custom
            None if the short code doesn't exist
        """
        url_obj = self.storage.get(short_code)
        
        if url_obj is None:
            return None
        
        return {
            "short_code": url_obj.short_code,
            "original_url": url_obj.original_url,
            "created_at": url_obj.created_at.isoformat(),
            "custom_code": url_obj.custom_code,
        }
    
    def get_all_urls(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all URLs.
        
        Returns:
            Dictionary mapping short codes to their information
        """
        all_urls = self.storage.get_all_urls()
        return {
            code: {
                "short_code": url.short_code,
                "original_url": url.original_url,
                "created_at": url.created_at.isoformat(),
                "custom_code": url.custom_code,
            }
            for code, url in all_urls.items()
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """
        Get global statistics for the shortener service.
        
        Returns:
            Dictionary containing:
            - total_urls: Total number of shortened URLs
            - total_accesses: Total number of URL accesses
            - most_accessed: List of most accessed URLs (short_code, count)
        """
        return {
            "total_urls": self.storage.count(),
            "total_accesses": self.stats.get_total_accesses(),
            "most_accessed": self.stats.get_most_accessed(limit=10),
        }
    
    def clear(self) -> None:
        """Clear all URLs and statistics."""
        self.storage.clear()
        self.stats.clear()
        self.generator.reset()