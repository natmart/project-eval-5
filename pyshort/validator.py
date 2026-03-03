"""URL validator module."""

import re
from typing import Optional
from urllib.parse import urlparse


class URLValidator:
    """Validates URLs and custom short codes."""

    # URL validation regex pattern
    URL_PATTERN = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:\S+(?::\S*)?@)?"  # optional user:pass@
        r"(?:"
        r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        r"\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])"
        r"\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])"
        r"\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])"
        r"|"  # ...or
        r"(?:(?:[a-zA-Z\u00a1-\uffff0-9]-*)*[a-zA-Z\u00a1-\uffff0-9]+)"
        r"(?:\.(?:[a-zA-Z\u00a1-\uffff0-9]-*)*[a-zA-Z\u00a1-\uffff0-9]+)*"
        r"(?:(?:\.(?:[a-zA-Z\u00a1-\uffff]{2,})))"
        r")"
        r"(?::\d{2,5})?"  # optional port
        r"(?:[/?#]\S*)?"  # resource path
        r"$",
        re.IGNORECASE,
    )

    # Reserved words that cannot be used as short codes
    RESERVED_WORDS = {"admin", "api", "health", "status", "metrics", "stats"}

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate a URL string.

        Args:
            url: The URL to validate.

        Returns:
            True if the URL is valid, False otherwise.
        """
        if not url or not isinstance(url, str):
            return False

        # Check with regex
        if not cls.URL_PATTERN.match(url):
            # Fallback: try basic URL parsing
            try:
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    return False
                return parsed.scheme in ("http", "https")
            except Exception:
                return False

        return True

    @classmethod
    def validate_custom_code(cls, code: str) -> bool:
        """Validate a custom short code.

        Args:
            code: The short code to validate.

        Returns:
            True if the code is valid, False otherwise.

        A valid code must:
        - Be non-empty
        - Contain only alphanumeric characters
        - Be between 1 and 100 characters
        - Not be a reserved word
        """
        if not code or not isinstance(code, str):
            return False

        if len(code) < 1 or len(code) > 100:
            return False

        if not code.isalnum():
            return False

        if code.lower() in cls.RESERVED_WORDS:
            return False

        return True