"""URL model class with serialization support."""

from datetime import datetime
from typing import Dict, Any, Optional


class URL:
    """Represents a shortened URL with metadata."""

    def __init__(
        self,
        original_url: str,
        short_code: str,
        created_at: Optional[datetime] = None,
        access_count: int = 0,
        is_custom: bool = False,
    ):
        """Initialize a URL object.

        Args:
            original_url: The original long URL.
            short_code: The short code for the URL.
            created_at: When the URL was created. Defaults to now.
            access_count: Number of times the URL has been accessed.
            is_custom: Whether the short code is custom or generated.
        """
        self.original_url = original_url
        self.short_code = short_code
        self.created_at = created_at or datetime.now()
        self.access_count = access_count
        self.is_custom = is_custom

    def to_dict(self) -> Dict[str, Any]:
        """Convert URL to dictionary for serialization.

        Returns:
            Dictionary representation of the URL.
        """
        return {
            "original_url": self.original_url,
            "short_code": self.short_code,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "is_custom": self.is_custom,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "URL":
        """Create URL from dictionary.

        Args:
            data: Dictionary containing URL data.

        Returns:
            A URL object.
        """
        created_at = None
        if "created_at" in data and data["created_at"]:
            created_at = datetime.fromisoformat(data["created_at"])

        return cls(
            original_url=data["original_url"],
            short_code=data["short_code"],
            created_at=created_at,
            access_count=data.get("access_count", 0),
            is_custom=data.get("is_custom", False),
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another URL object."""
        if not isinstance(other, URL):
            return False
        return (
            self.original_url == other.original_url
            and self.short_code == other.short_code
        )

    def __repr__(self) -> str:
        """String representation of URL."""
        return f"URL(short_code='{self.short_code}', original_url='{self.original_url}')"