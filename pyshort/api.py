"""Main URLShortener API facade."""

from typing import Optional, Dict, Any, List

from pyshort.model import URL
from pyshort.validator import URLValidator
from pyshort.generator import CodeGenerator
from pyshort.storage import Storage
from pyshort.stats import Statistics


class URLShortener:
    """Main URL shortener API facade."""

    def __init__(
        self,
        persist_urls: Optional[str] = None,
        persist_stats: Optional[str] = None,
        code_length: int = 6,
    ):
        """Initialize the URL shortener.

        Args:
            persist_urls: Optional file path for URL persistence.
            persist_stats: Optional file path for statistics persistence.
            code_length: Default length for generated short codes.
        """
        self.validator = URLValidator()
        self.generator = CodeGenerator(code_length=code_length)
        self.storage = Storage(persist_file=persist_urls)
        self.stats = Statistics(persist_file=persist_stats)

        # Sync generator with existing codes
        for url in self.storage.get_all():
            if url.short_code not in self.generator._generated_codes:
                self.generator._generated_codes.add(url.short_code)

    def shorten(self, url: str, custom_code: Optional[str] = None) -> tuple[str, URL]:
        """Shorten a URL.

        Args:
            url: The original URL to shorten.
            custom_code: Optional custom short code.

        Returns:
            Tuple of (short_code, URL object).

        Raises:
            ValueError: If the URL or custom code is invalid.
        """
        # Validate URL
        if not self.validator.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        # Use custom code if provided
        if custom_code:
            if not self.validator.validate_custom_code(custom_code):
                raise ValueError(f"Invalid custom code: {custom_code}")
            if self.storage.exists(custom_code):
                raise ValueError(f"Short code already exists: {custom_code}")

            short_code = self.generator.set_custom_code(custom_code)
            is_custom = True
        else:
            # Generate a random code
            short_code = self.generator.generate_random()
            is_custom = False

        # Create and store the URL
        url_obj = URL(
            original_url=url,
            short_code=short_code,
            is_custom=is_custom,
        )
        self.storage.add(url_obj)

        return short_code, url_obj

    def resolve(self, short_code: str) -> Optional[str]:
        """Resolve a short code to its original URL.

        Args:
            short_code: The short code to resolve.

        Returns:
            The original URL if found, None otherwise.
        """
        url_obj = self.storage.get(short_code)
        if url_obj:
            # Increment access count
            self.stats.increment(short_code)
            return url_obj.original_url
        return None

    def get_stats(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a short code.

        Args:
            short_code: The short code to get stats for.

        Returns:
            Dictionary containing statistics or None if not found.
        """
        url_obj = self.storage.get(short_code)
        if not url_obj:
            return None

        access_count = self.stats.get_access_count(short_code)
        access_history = self.stats.get_access_history(short_code)

        return {
            "short_code": short_code,
            "original_url": url_obj.original_url,
            "created_at": url_obj.created_at.isoformat(),
            "is_custom": url_obj.is_custom,
            "access_count": access_count,
            "access_history": [ts.isoformat() for ts in access_history],
        }

    def delete(self, short_code: str) -> bool:
        """Delete a URL by its short code.

        Args:
            short_code: The short code to delete.

        Returns:
            True if the URL was deleted, False if it didn't exist.
        """
        if not self.storage.exists(short_code):
            return False

        self.storage.delete(short_code)
        self.stats.delete(short_code)

        # Note: We don't remove from generator._generated_codes
        # to prevent reusing the same code
        return True

    def exists(self, short_code: str) -> bool:
        """Check if a short code exists.

        Args:
            short_code: The short code to check.

        Returns:
            True if the short code exists, False otherwise.
        """
        return self.storage.exists(short_code)

    def get_url_info(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Get information about a URL without incrementing access count.

        Args:
            short_code: The short code to look up.

        Returns:
            Dictionary containing URL info or None if not found.
        """
        url_obj = self.storage.get(short_code)
        if not url_obj:
            return None

        return url_obj.to_dict()

    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get information about all URLs.

        Returns:
            List of dictionaries containing URL information.
        """
        return [url.to_dict() for url in self.storage.get_all()]

    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics across all URLs.

        Returns:
            Dictionary containing global statistics.
        """
        return {
            "total_urls": self.storage.count(),
            "total_accesses": self.stats.get_total_accesses(),
            "urls_with_accesses": self.stats.get_url_count(),
        }

    def clear(self) -> None:
        """Clear all URLs and statistics."""
        self.storage.clear()
        self.stats.clear()
        self.generator.clear_history()