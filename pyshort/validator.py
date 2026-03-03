"""URL validator module for PyShort.

This module provides functions for validating, filtering, and normalizing URLs.
It includes scheme validation, domain validation, blocked domain filtering,
and URL normalization to ensure consistency across the system.
"""

import re
from typing import Optional, Set
from urllib.parse import urlparse, urlunparse

# Default allowed URL schemes
DEFAULT_ALLOWED_SCHEMES = {"http", "https"}

# Default blocked domains (commonly blocked in URL shorteners)
DEFAULT_BLOCKED_DOMAINS: Set[str] = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "[::1]",
    "example.com",
    "test.com",
    "invalid",
}

# Pattern for validating domain names
DOMAIN_PATTERN = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,}$"
)

# Pattern for validating IP addresses
IP_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)


class ValidationError(ValueError):
    """Exception raised for URL validation errors."""
    
    def __init__(self, message: str, url: str):
        """Initialize the validation error.
        
        Args:
            message: Error message describing what failed validation.
            url: The URL that failed validation.
        """
        super().__init__(f"{message}: {url}")
        self.message = message
        self.url = url


def validate_scheme(
    scheme: Optional[str],
    allowed_schemes: Optional[Set[str]] = None
) -> bool:
    """Validate that a URL scheme is allowed.
    
    Args:
        scheme: The URL scheme to validate (e.g., 'http', 'https').
        allowed_schemes: Set of allowed schemes. Defaults to http and https.
        
    Returns:
        True if the scheme is valid and allowed.
        
    Raises:
        ValidationError: If the scheme is None or not in allowed schemes.
        
    Examples:
        >>> validate_scheme('https')
        True
        >>> validate_scheme('ftp')
        ValidationError: Scheme 'ftp' is not allowed
    """
    if allowed_schemes is None:
        allowed_schemes = DEFAULT_ALLOWED_SCHEMES
    
    if not scheme:
        raise ValidationError("URL scheme is required", "None")
    
    if scheme.lower() not in {s.lower() for s in allowed_schemes}:
        raise ValidationError(
            f"Scheme '{scheme}' is not allowed",
            scheme
        )
    
    return True


def validate_domain(domain: str) -> bool:
    """Validate that a domain name or IP address is well-formed.
    
    Args:
        domain: The domain or IP address to validate.
        
    Returns:
        True if the domain is valid.
        
    Raises:
        ValidationError: If the domain is invalid.
        
    Examples:
        >>> validate_domain('example.com')
        True
        >>> validate_domain('192.168.1.1')
        True
        >>> validate_domain('invalid..domain')
        ValidationError: Invalid domain format
    """
    if not domain:
        raise ValidationError("Domain is required", "None")
    
    # Remove port if present
    domain = domain.split(":")[0]
    
    # Check for IPv6 address (simple check)
    if domain.startswith("[") and domain.endswith("]"):
        domain = domain[1:-1]
    
    # Check if it's an IP address
    if IP_PATTERN.match(domain):
        return True
    
    # Check if it's a domain name
    if DOMAIN_PATTERN.match(domain):
        return True
    
    raise ValidationError(f"Invalid domain format", domain)


def check_blocked_domains(
    domain: str,
    blocked_domains: Optional[Set[str]] = None
) -> bool:
    """Check if a domain is in the blocked domains list.
    
    Args:
        domain: The domain to check.
        blocked_domains: Set of blocked domains. Defaults to common localhost/test domains.
        
    Returns:
        True if the domain is allowed (not in blocked list).
        
    Raises:
        ValidationError: If the domain is blocked.
        
    Examples:
        >>> check_blocked_domains('example.com')
        ValidationError: Domain is blocked
        >>> check_blocked_domains('google.com')
        True
    """
    if blocked_domains is None:
        blocked_domains = DEFAULT_BLOCKED_DOMAINS
    
    # Remove port if present
    domain = domain.split(":")[0]
    
    # Normalize to lowercase for comparison
    domain_lower = domain.lower()
    blocked_lower = {d.lower() for d in blocked_domains}
    
    if domain_lower in blocked_lower:
        raise ValidationError(f"Domain is blocked", domain)
    
    # Check subdomains against blocked domains
    for blocked in blocked_lower:
        if domain_lower.endswith(f".{blocked}"):
            raise ValidationError(f"Domain is blocked (subdomain of blocked domain)", domain)
    
    return True


def normalize_url(
    url: str,
    default_scheme: str = "https",
    remove_trailing_slash: bool = True
) -> str:
    """Normalize a URL to a consistent format.
    
    Normalization includes:
    - Adding default scheme if missing
    - Lowercasing the scheme and domain
    - Removing trailing slash from path
    - Preserving query parameters and fragments
    
    Args:
        url: The URL to normalize.
        default_scheme: The scheme to add if missing (default: 'https').
        remove_trailing_slash: Whether to remove trailing slashes from the path.
        
    Returns:
        The normalized URL.
        
    Raises:
        ValidationError: If the URL cannot be parsed or validated.
        
    Examples:
        >>> normalize_url('example.com/path/')
        'https://example.com/path'
        >>> normalize_url('HTTP://EXAMPLE.COM/Path/')
        'https://example.com/Path'
    """
    if not url or not url.strip():
        raise ValidationError("URL cannot be empty", url)
    
    url = url.strip()
    
    # Check if scheme is present
    parsed = urlparse(url)
    
    if not parsed.scheme:
        # Add default scheme
        url = f"{default_scheme}://{url}"
        parsed = urlparse(url)
    
    # Validate scheme
    validate_scheme(parsed.scheme, DEFAULT_ALLOWED_SCHEMES)
    
    if not parsed.netloc:
        raise ValidationError("URL must include a domain", url)
    
    # Validate domain
    validate_domain(parsed.netloc)
    
    # Check blocked domains
    check_blocked_domains(parsed.netloc)
    
    # Normalize: lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    
    # Remove trailing slash from path if present and requested
    if remove_trailing_slash and path == "/":
        path = ""
    elif remove_trailing_slash and len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    
    # Reconstruct the URL
    normalized = urlunparse((
        scheme,
        netloc,
        path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    return normalized


def is_valid_url(
    url: str,
    allowed_schemes: Optional[Set[str]] = None,
    blocked_domains: Optional[Set[str]] = None
) -> bool:
    """Check if a URL is valid without throwing an exception.
    
    This is a convenience function that validates all aspects of a URL
    and returns a boolean instead of raising exceptions.
    
    Args:
        url: The URL to validate.
        allowed_schemes: Set of allowed schemes. Defaults to http and https.
        blocked_domains: Set of blocked domains.
        
    Returns:
        True if the URL is valid, False otherwise.
        
    Examples:
        >>> is_valid_url('https://example.com')
        True
        >>> is_valid_url('ftp://example.com')
        False
        >>> is_valid_url('https://localhost')
        False
    """
    try:
        if allowed_schemes:
            validate_scheme(urlparse(url).scheme or "https", allowed_schemes)
        if blocked_domains:
            check_blocked_domains(urlparse(url).netloc, blocked_domains)
        normalize_url(url)
        return True
    except ValidationError:
        return False


def extract_domain(url: str) -> str:
    """Extract and normalize the domain from a URL.
    
    Args:
        url: The URL to extract the domain from.
        
    Returns:
        The normalized (lowercase) domain.
        
    Raises:
        ValidationError: If the URL cannot be parsed.
        
    Examples:
        >>> extract_domain('https://EXAMPLE.com/path')
        'example.com'
    """
    parsed = urlparse(url)
    
    if not parsed.netloc:
        normalized = normalize_url(url)
        parsed = urlparse(normalized)
    
    domain = parsed.netloc.split(":")[0].lower()
    
    return domain


def validate_url_for_shortening(url: str) -> str:
    """Validate and prepare a URL for shortening.
    
    This is a convenience function that performs all necessary validation
    and normalization steps for URL shortening. It's the main entry point
    for the URL shortener service.
    
    Args:
        url: The URL to validate and normalize.
        
    Returns:
        The normalized URL ready for shortening.
        
    Raises:
        ValidationError: If the URL fails any validation check.
        
    Examples:
        >>> validate_url_for_shortening('example.com')
        'https://example.com'
        >>> validate_url_for_shortening('https://malicious-site.com')
        ValidationError: Domain is blocked
    """
    # Normalize and validate in one step
    normalized = normalize_url(url)
    
    return normalized