"""URL model class for PyShort."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


@dataclass
class URL:
    """Model representing a shortened URL."""
    
    short_code: str
    original_url: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed_at: datetime | None = None
    custom_code: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert URL model to dictionary."""
        return {
            "short_code": self.short_code,
            "original_url": self.original_url,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "custom_code": self.custom_code,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "URL":
        """Create URL model from dictionary."""
        return cls(
            short_code=data["short_code"],
            original_url=data["original_url"],
            created_at=datetime.fromisoformat(data["created_at"]),
            access_count=data.get("access_count", 0),
            last_accessed_at=datetime.fromisoformat(data["last_accessed_at"]) if data.get("last_accessed_at") else None,
            custom_code=data.get("custom_code", False),
        )