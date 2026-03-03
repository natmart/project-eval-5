"""URL validator module for PyShort."""

import re
from urllib.parse import urlparse


class URLValidator:
    """Validator for checking URL validity."""
    
    # Basic URL pattern regex
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP address
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    def validate(self, url: str) -> bool:
        """
        Validate if the given string is a valid URL.
        
        Args:
            url: The URL string to validate
            
        Returns:
            True if the URL is valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        if not url:
            return False
        
        # Check basic URL pattern
        if not self.URL_PATTERN.match(url):
            return False
        
        # Parse the URL to ensure it's well-formed
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            if parsed.scheme not in ('http', 'https'):
                return False
        except Exception:
            return False
        
        return True
    
    def validate_short_code(self, short_code: str, min_length: int = 4, max_length: int = 20) -> bool:
        """
        Validate a short code is safe to use.
        
        Args:
            short_code: The short code to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            
        Returns:
            True if the short code is valid, False otherwise
        """
        if not short_code or not isinstance(short_code, str):
            return False
        
        short_code = short_code.strip()
        
        if not short_code:
            return False
        
        if len(short_code) < min_length or len(short_code) > max_length:
            return False
        
        # Only allow alphanumeric characters and hyphens
        if not re.match(r'^[a-zA-Z0-9-]+$', short_code):
            return False
        
        # Don't allow codes that are just numbers or could be confused
        if short_code.isdigit():
            return False
        
        # Don't allow reserved codes
        reserved_codes = {'api', 'admin', 'stats', 'help', 'about', 'www', 'test'}
        if short_code.lower() in reserved_codes:
            return False
        
        return True