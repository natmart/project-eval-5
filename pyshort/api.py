"""URL Shortener API facade.

This module provides the main URLShortener class that serves as the public
interface for the PyShort library.
"""

from pyshort.generator import CodeGenerator


class URLShortener:
    """Main URL shortener class that provides the public API.

    This class allows users to shorten URLs and resolve them back to their
    original form using short codes.
    """

    def __init__(self):
        """Initialize a new URLShortener instance."""
        self._generator = CodeGenerator()
        self._urls = {}

    def shorten(self, url: str, custom_code: str = None) -> str:
        """Shorten a URL and return the short code.

        Args:
            url: The URL to shorten.
            custom_code: Optional custom short code. If not provided,
                        a random code will be generated.

        Returns:
            The short code that can be used to retrieve the original URL.

        Raises:
            ValueError: If the URL is invalid or the custom code is invalid.
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        if custom_code is not None:
            code = self._generator.set_custom_code(custom_code)
        else:
            code = self._generator.generate_random()

        self._urls[code] = url
        return code

    def resolve(self, short_code: str) -> str:
        """Resolve a short code to the original URL.

        Args:
            short_code: The short code to resolve.

        Returns:
            The original URL.

        Raises:
            KeyError: If the short code does not exist.
        """
        if short_code not in self._urls:
            raise KeyError(f"Short code '{short_code}' not found")
        return self._urls[short_code]

    def exists(self, short_code: str) -> bool:
        """Check if a short code exists.

        Args:
            short_code: The short code to check.

        Returns:
            True if the short code exists, False otherwise.
        """
        return short_code in self._urls

    def get_url_info(self, short_code: str):
        """Get information about a shortened URL.

        Args:
            short_code: The short code to look up.

        Returns:
            A dictionary containing URL information.

        Raises:
            KeyError: If the short code does not exist.
        """
        if short_code not in self._urls:
            raise KeyError(f"Short code '{short_code}' not found")
        return {"code": short_code, "url": self._urls[short_code]}

    def get_all_urls(self):
        """Get all shortened URLs.

        Returns:
            A list of dictionaries containing all URL information.
        """
        return [
            {"code": code, "url": url} for code, url in self._urls.items()
        ]

    def delete(self, short_code: str) -> bool:
        """Delete a shortened URL.

        Args:
            short_code: The short code to delete.

        Returns:
            True if the URL was deleted, False if it didn't exist.
        """
        if short_code in self._urls:
            del self._urls[short_code]
            return True
        return False

    def clear(self):
        """Clear all shortened URLs."""
        self._urls.clear()
        self._generator.clear_history()