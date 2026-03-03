"""Statistics tracking module."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class Statistics:
    """Tracks URL access counts and timestamps."""

    def __init__(self, persist_file: Optional[str] = None):
        """Initialize statistics tracker.

        Args:
            persist_file: Optional file path for JSON persistence.
        """
        self._access_counts: Dict[str, int] = {}
        self._access_history: Dict[str, List[datetime]] = {}
        self._persist_file = persist_file

        if persist_file:
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Load statistics from persistence file."""
        if not self._persist_file or not os.path.exists(self._persist_file):
            return

        try:
            with open(self._persist_file, "r") as f:
                data = json.load(f)
                self._access_counts = data.get("access_counts", {})
                self._access_history = {
                    short_code: [
                        datetime.fromisoformat(ts_str)
                        for ts_str in timestamps
                    ]
                    for short_code, timestamps in data.get("access_history", {}).items()
                }
        except Exception:
            # If loading fails, start fresh
            self._access_counts = {}
            self._access_history = {}

    def _save_to_file(self) -> None:
        """Save statistics to persistence file."""
        if not self._persist_file:
            return

        try:
            # Create parent directories if needed
            Path(self._persist_file).parent.mkdir(parents=True, exist_ok=True)

            with open(self._persist_file, "w") as f:
                data = {
                    "access_counts": self._access_counts,
                    "access_history": {
                        short_code: [ts.isoformat() for ts in timestamps]
                        for short_code, timestamps in self._access_history.items()
                    },
                }
                json.dump(data, f)
        except Exception:
            # If saving fails, continue without persistence
            pass

    def increment(self, short_code: str) -> None:
        """Increment access count for a short code.

        Args:
            short_code: The short code to track.
        """
        self._access_counts[short_code] = self._access_counts.get(short_code, 0) + 1

        if short_code not in self._access_history:
            self._access_history[short_code] = []
        self._access_history[short_code].append(datetime.now())

        self._save_to_file()

    def get_access_count(self, short_code: str) -> int:
        """Get access count for a short code.

        Args:
            short_code: The short code to query.

        Returns:
            Number of accesses for the short code.
        """
        return self._access_counts.get(short_code, 0)

    def get_access_history(self, short_code: str) -> List[datetime]:
        """Get access history for a short code.

        Args:
            short_code: The short code to query.

        Returns:
            List of timestamps when the URL was accessed.
        """
        return self._access_history.get(short_code, []).copy()

    def delete(self, short_code: str) -> None:
        """Delete statistics for a short code.

        Args:
            short_code: The short code to delete.
        """
        self._access_counts.pop(short_code, None)
        self._access_history.pop(short_code, None)
        self._save_to_file()

    def clear(self) -> None:
        """Clear all statistics."""
        self._access_counts.clear()
        self._access_history.clear()
        self._save_to_file()

    def get_total_accesses(self) -> int:
        """Get total access count across all URLs.

        Returns:
            Total number of URL accesses.
        """
        return sum(self._access_counts.values())

    def get_url_count(self) -> int:
        """Get number of URLs being tracked.

        Returns:
            Number of unique short codes with statistics.
        """
        return len(self._access_counts)

    def get_all_stats(self) -> Dict[str, Dict[str, any]]:
        """Get statistics for all URLs.

        Returns:
            Dictionary mapping short codes to their stats.
        """
        return {
            short_code: {
                "access_count": self._access_counts.get(short_code, 0),
                "access_history_size": len(self._access_history.get(short_code, [])),
            }
            for short_code in set(
                list(self._access_counts.keys()) + list(self._access_history.keys())
            )
        }