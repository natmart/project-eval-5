"""Statistics tracking module for PyShort."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path


class Stats:
    """Statistics tracker for URL access and usage."""
    
    def __init__(self, storage_path: str | None = None):
        """
        Initialize the statistics tracker.
        
        Args:
            storage_path: Optional path to a JSON file for persistence
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.stats: Dict[str, Dict] = {}
        self._load_from_file()
    
    def record_access(self, short_code: str) -> None:
        """
        Record an access to a URL.
        
        Args:
            short_code: The short code that was accessed
        """
        if short_code not in self.stats:
            self.stats[short_code] = {
                "access_count": 0,
                "first_accessed_at": None,
                "last_accessed_at": None,
                "access_history": [],
            }
        
        now = datetime.utcnow()
        
        self.stats[short_code]["access_count"] += 1
        self.stats[short_code]["last_accessed_at"] = now.isoformat()
        
        if self.stats[short_code]["first_accessed_at"] is None:
            self.stats[short_code]["first_accessed_at"] = now.isoformat()
        
        # Keep recent access history (last 100)
        self.stats[short_code]["access_history"].append(now.isoformat())
        if len(self.stats[short_code]["access_history"]) > 100:
            self.stats[short_code]["access_history"] = self.stats[short_code]["access_history"][-100:]
        
        self._save_to_file()
    
    def get_stats(self, short_code: str) -> Optional[Dict]:
        """
        Get statistics for a specific URL.
        
        Args:
            short_code: The short code to get stats for
            
        Returns:
            Dictionary with statistics or None if not found
        """
        return self.stats.get(short_code)
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all URLs.
        
        Returns:
            Dictionary mapping short codes to their statistics
        """
        return self.stats.copy()
    
    def get_access_count(self, short_code: str) -> int:
        """
        Get the access count for a specific URL.
        
        Args:
            short_code: The short code to get the count for
            
        Returns:
            The access count, or 0 if not found
        """
        if short_code in self.stats:
            return self.stats[short_code]["access_count"]
        return 0
    
    def get_most_accessed(self, limit: int = 10) -> List[tuple[str, int]]:
        """
        Get the most accessed URLs, sorted by access count.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of tuples (short_code, access_count), sorted by count descending
        """
        sorted_urls = sorted(
            self.stats.items(),
            key=lambda x: x[1]["access_count"],
            reverse=True
        )
        return [(code, data["access_count"]) for code, data in sorted_urls[:limit]]
    
    def get_recent_accesses(self, short_code: str, limit: int = 10) -> List[str]:
        """
        Get recent access timestamps for a URL.
        
        Args:
            short_code: The short code to get accesses for
            limit: Maximum number of timestamps to return
            
        Returns:
            List of ISO format timestamps, most recent first
        """
        if short_code not in self.stats:
            return []
        
        history = self.stats[short_code]["access_history"]
        return history[-limit:][::-1]
    
    def get_total_accesses(self) -> int:
        """
        Get the total number of URL accesses across all URLs.
        
        Returns:
            The total access count
        """
        return sum(data["access_count"] for data in self.stats.values())
    
    def get_total_urls(self) -> int:
        """
        Get the total number of URLs that have been accessed.
        
        Returns:
            The count of URLs with access statistics
        """
        return len(self.stats)
    
    def delete_stats(self, short_code: str) -> bool:
        """
        Delete statistics for a URL.
        
        Args:
            short_code: The short code to delete stats for
            
        Returns:
            True if deleted, False if not found
        """
        if short_code in self.stats:
            del self.stats[short_code]
            self._save_to_file()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all statistics."""
        self.stats.clear()
        self._save_to_file()
    
    def _save_to_file(self) -> None:
        """Save statistics to file if storage_path is configured."""
        if not self.storage_path:
            return
        
        try:
            # Ensure parent directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception:
            # Silently fail on storage errors
            pass
    
    def _load_from_file(self) -> None:
        """Load statistics from file if storage_path exists."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                self.stats = json.load(f)
        except Exception:
            # Start fresh if loading fails
            self.stats.clear()