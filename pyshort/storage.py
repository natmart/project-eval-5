"""Storage module for persistence."""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path

from pyshort.model import URL


class Storage:
    """In-memory storage of URL objects with optional file persistence."""

    def __init__(self, persist_file: Optional[str] = None):
        """Initialize storage.

        Args:
            persist_file: Optional file path for JSON persistence.
        """
        self._urls: Dict[str, URL] = {}
        self._persist_file = persist_file

        if persist_file:
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Load URLs from persistence file."""
        if not self._persist_file or not os.path.exists(self._persist_file):
            return

        try:
            with open(self._persist_file, "r") as f:
                data = json.load(f)
                for short_code, url_data in data.items():
                    self._urls[short_code] = URL.from_dict(url_data)
        except Exception:
            # If loading fails, start fresh
            self._urls = {}

    def _save_to_file(self) -> None:
        """Save URLs to persistence file."""
        if not self._persist_file:
            return

        try:
            # Create parent directories if needed
            Path(self._persist_file).parent.mkdir(parents=True, exist_ok=True)

            with open(self._persist_file, "w") as f:
                data = {
                    short_code: url.to_dict()
                    for short_code, url in self._urls.items()
                }
                json.dump(data, f)
        except Exception:
            # If saving fails, continue without persistence
            pass

    def add(self, url: URL) -> None:
        """Add a URL to storage.

        Args:
            url: The URL object to add.
        """
        self._urls[url.short_code] = url
        self._save_to_file()

    def get(self, short_code: str) -> Optional[URL]:
        """Get a URL by short code.

        Args:
            short_code: The short code to look up.

        Returns:
            The URL object if found, None otherwise.
        """
        return self._urls.get(short_code)

    def exists(self, short_code: str) -> bool:
        """Check if a short code exists.

        Args:
            short_code: The short code to check.

        Returns:
            True if the short code exists, False otherwise.
        """
        return short_code in self._urls

    def get_all(self) -> List[URL]:
        """Get all URLs.

        Returns:
            List of all URL objects.
        """
        return list(self._urls.values())

    def delete(self, short_code: str) -> bool:
        """Delete a URL by short code.

        Args:
            short_code: The short code to delete.

        Returns:
            True if the URL was deleted, False if it didn't exist.
        """
        if short_code in self._urls:
            del self._urls[short_code]
            self._save_to_file()
            return True
        return False

    def clear(self) -> None:
        """Clear all URLs from storage."""
        self._urls.clear()
        self._save_to_file()

    def count(self) -> int:
        """Get the number of stored URLs.

        Returns:
            Number of URLs in storage.
        """
        return len(self._urls)