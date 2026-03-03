"""Tests for the URL validator module."""

import pytest

from pyshort.validator import (
    ValidationError,
    validate_scheme,
    validate_domain,
    check_blocked_domains,
    normalize_url,
    is_valid_url,
    extract_domain,
    validate_url_for_shortening,
    DEFAULT_ALLOWED_SCHEMES,
    DEFAULT_BLOCKED_DOMAINS,
)


class TestValidateScheme:
    """Tests for validate_scheme function."""
    
    def test_valid_schemes(self):
        """Test that valid schemes are accepted."""
        assert validate_scheme("http") is True
        assert validate_scheme("https") is True
        assert validate_scheme("HTTP") is True
        assert validate_scheme("HTTPS") is True
    
    def test_custom_allowed_schemes(self):
        """Test custom allowed schemes."""
        custom_schemes = {"http", "https", "ftp"}
        assert validate_scheme("ftp", custom_schemes) is True
        assert validate_scheme("http", custom_schemes) is True
    
    def test_invalid_scheme(self):
        """Test that invalid schemes are rejected."""
        with pytest.raises(ValidationError, match="Scheme 'ftp' is not allowed"):
            validate_scheme("ftp")
        
        with pytest.raises(ValidationError, match="Scheme 'mailto' is not allowed"):
            validate_scheme("mailto")
    
    def test_none_scheme(self):
        """Test that None scheme is rejected."""
        with pytest.raises(ValidationError, match="URL scheme is required"):
            validate_scheme(None)
    
    def test_empty_scheme(self):
        """Test that empty scheme is rejected."""
        with pytest.raises(ValidationError, match="URL scheme is required"):
            validate_scheme("")


class TestValidateDomain:
    """Tests for validate_domain function."""
    
    def test_valid_domains(self):
        """Test that valid domains are accepted."""
        assert validate_domain("example.com") is True
        assert validate_domain("sub.example.com") is True
        assert validate_domain("deep.sub.example.com") is True
        assert validate_domain("my-site.com") is True
        assert validate_domain("site123.com") is True
    
    def test_valid_ip_addresses(self):
        """Test that valid IP addresses are accepted."""
        assert validate_domain("192.168.1.1") is True
        assert validate_domain("10.0.0.1") is True
        assert validate_domain("255.255.255.255") is True
        assert validate_domain("0.0.0.0") is True
    
    def test_domain_with_port(self):
        """Test that domain with port is handled."""
        assert validate_domain("example.com:8080") is True
        assert validate_domain("192.168.1.1:443") is True
    
    def test_ipv6_simple(self):
        """Test simple IPv6 address handling."""
        # IPv6 addresses with brackets
        assert validate_domain("[::1]") is True
    
    def test_invalid_domains(self):
        """Test that invalid domains are rejected."""
        with pytest.raises(ValidationError, match="Invalid domain format"):
            validate_domain("invalid")
        
        with pytest.raises(ValidationError, match="Invalid domain format"):
            validate_domain("invalid..com")
        
        with pytest.raises(ValidationError, match="Invalid domain format"):
            validate_domain(".example.com")
        
        with pytest.raises(ValidationError, match="Invalid domain format"):
            validate_domain("example.com.")
    
    def test_invalid_ip_addresses(self):
        """Test that invalid IP addresses are rejected."""
        with pytest.raises(ValidationError, match="Invalid domain format"):
            validate_domain("256.1.1.1")
        
        with pytest.raises(ValidationError, match="Invalid domain format"):
            validate_domain("192.168.1")
        
        with pytest.raises(ValidationError, match="Invalid domain format"):
            validate_domain("192.168.1.1.1")
    
    def test_empty_domain(self):
        """Test that empty domain is rejected."""
        with pytest.raises(ValidationError, match="Domain is required"):
            validate_domain("")
        
        with pytest.raises(ValidationError, match="Domain is required"):
            validate_domain(None)


class TestCheckBlockedDomains:
    """Tests for check_blocked_domains function."""
    
    def test_allowed_domain(self):
        """Test that allowed domains pass."""
        assert check_blocked_domains("google.com") is True
        assert check_blocked_domains("example.org") is True
        assert check_blocked_domains("sub.domain.com") is True
    
    def test_blocked_domain_exact(self):
        """Test that exactly blocked domains are rejected."""
        with pytest.raises(ValidationError, match="Domain is blocked"):
            check_blocked_domains("localhost")
        
        with pytest.raises(ValidationError, match="Domain is blocked"):
            check_blocked_domains("example.com")
        
        with pytest.raises(ValidationError, match="Domain is blocked"):
            check_blocked_domains("test.com")
    
    def test_blocked_domain_subdomain(self):
        """Test that subdomains of blocked domains are rejected."""
        with pytest.raises(ValidationError, match="Domain is blocked.*subdomain"):
            check_blocked_domains("sub.localhost")
        
        with pytest.raises(ValidationError, match="Domain is blocked.*subdomain"):
            check_blocked_domains("api.localhost")
    
    def test_custom_blocked_domains(self):
        """Test custom blocked domain list."""
        custom_blocked = {"malicious.com", "spam.net"}
        
        assert check_blocked_domains("good.com", custom_blocked) is True
        
        with pytest.raises(ValidationError, match="Domain is blocked"):
            check_blocked_domains("malicious.com", custom_blocked)
        
        with pytest.raises(ValidationError, match="Domain is blocked.*subdomain"):
            check_blocked_domains("sub.malicious.com", custom_blocked)
    
    def test_blocked_domain_with_port(self):
        """Test that blocked domains with port are rejected."""
        with pytest.raises(ValidationError, match="Domain is blocked"):
            check_blocked_domains("localhost:8080")
        
        with pytest.raises(ValidationError, match="Domain is blocked"):
            check_blocked_domains("example.com:443")
    
    def test_case_insensitive(self):
        """Test that blocking is case-insensitive."""
        with pytest.raises(ValidationError, match="Domain is blocked"):
            check_blocked_domains("LOCALHOST")
        
        with pytest.raises(ValidationError, match="Domain is blocked"):
            check_blocked_domains("Example.Com")


class TestNormalizeUrl:
    """Tests for normalize_url function."""
    
    def test_add_default_scheme(self):
        """Test that default scheme is added when missing."""
        assert normalize_url("example.com") == "https://example.com"
        assert normalize_url("google.com/path") == "https://google.com/path"
    
    def test_preserve_existing_scheme(self):
        """Test that existing schemes are preserved."""
        assert normalize_url("http://example.com") == "http://example.com"
        assert normalize_url("https://example.com") == "https://example.com"
    
    def test_lowercase_scheme(self):
        """Test that scheme is lowercased."""
        assert normalize_url("HTTP://example.com") == "http://example.com"
        assert normalize_url("HTTPS://example.com") == "https://example.com"
    
    def test_lowercase_domain(self):
        """Test that domain is lowercased."""
        assert normalize_url("https://EXAMPLE.COM") == "https://example.com"
        assert normalize_url("https://ExAmPlE.CoM") == "https://example.com"
    
    def test_remove_trailing_slash(self):
        """Test trailing slash removal."""
        assert normalize_url("https://example.com/") == "https://example.com"
        assert normalize_url("https://example.com/path/") == "https://example.com/path"
        assert normalize_url("https://example.com/path/sub/") == "https://example.com/path/sub"
    
    def test_preserve_trailing_slash_when_disabled(self):
        """Test that trailing slash is preserved when option is disabled."""
        result = normalize_url("https://example.com/", remove_trailing_slash=False)
        assert result == "https://example.com/"
        
        result = normalize_url("https://example.com/path/", remove_trailing_slash=False)
        assert result == "https://example.com/path/"
    
    def test_preserve_query_parameters(self):
        """Test that query parameters are preserved."""
        assert normalize_url("https://example.com?foo=bar") == "https://example.com?foo=bar"
        assert normalize_url("https://example.com/path?x=1&y=2") == "https://example.com/path?x=1&y=2"
    
    def test_preserve_fragment(self):
        """Test that fragments are preserved."""
        assert normalize_url("https://example.com#section") == "https://example.com#section"
        assert normalize_url("https://example.com/path#anchor") == "https://example.com/path#anchor"
    
    def test_preserve_both_query_and_fragment(self):
        """Test that both query and fragment are preserved."""
        assert normalize_url("https://example.com?q=1#section") == "https://example.com?q=1#section"
    
    def test_normalization_chain(self):
        """Test multiple normalizations applied together."""
        url = "HTTP://EXAMPLE.COM/Path/?q=Test#Anchor"
        expected = "http://example.com/Path?q=Test#Anchor"
        assert normalize_url(url) == expected
    
    def test_custom_default_scheme(self):
        """Test custom default scheme."""
        assert normalize_url("example.com", default_scheme="http") == "http://example.com"
    
    def test_invalid_scheme(self):
        """Test that invalid scheme raises error."""
        with pytest.raises(ValidationError, match="Scheme 'ftp' is not allowed"):
            normalize_url("ftp://example.com")
    
    def test_empty_url(self):
        """Test that empty URL raises error."""
        with pytest.raises(ValidationError, match="URL cannot be empty"):
            normalize_url("")
        
        with pytest.raises(ValidationError, match="URL cannot be empty"):
            normalize_url("   ")
    
    def test_missing_domain(self):
        """Test that URL without domain raises error."""
        with pytest.raises(ValidationError, match="URL must include a domain"):
            normalize_url("https://")
    
    def test_blocked_domain(self):
        """Test that blocked domains raise error."""
        with pytest.raises(ValidationError, match="Domain is blocked"):
            normalize_url("localhost")


class TestIsValidUrl:
    """Tests for is_valid_url function."""
    
    def test_valid_urls(self):
        """Test that valid URLs return True."""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://google.com/path") is True
        assert is_valid_url("example.com") is True
    
    def test_invalid_schemes(self):
        """Test that URLs with invalid schemes return False."""
        assert is_valid_url("ftp://example.com") is False
        assert is_valid_url("mailto://test@example.com") is False
    
    def test_blocked_domains(self):
        """Test that blocked domains return False."""
        assert is_valid_url("localhost") is False
        assert is_valid_url("https://example.com") is False
        assert is_valid_url("http://localhost:8080") is False
    
    def test_custom_allowed_schemes(self):
        """Test custom allowed schemes."""
        assert is_valid_url("ftp://example.com", allowed_schemes={"http", "https", "ftp"}) is True
        assert is_valid_url("ftp://example.com", allowed_schemes={"http", "https"}) is False
    
    def test_custom_blocked_domains(self):
        """Test custom blocked domains."""
        assert is_valid_url("https://malicious.com", blocked_domains={"malicious.com"}) is False
        assert is_valid_url("https://malicious.com", blocked_domains={"other.com"}) is True


class TestExtractDomain:
    """Tests for extract_domain function."""
    
    def test_extract_domain_from_url(self):
        """Test domain extraction from full URL."""
        assert extract_domain("https://example.com") == "example.com"
        assert extract_domain("http://google.com/path") == "google.com"
        assert extract_domain("https://sub.example.com/path?query=1") == "sub.example.com"
    
    def test_extract_domain_with_port(self):
        """Test domain extraction with port."""
        assert extract_domain("https://example.com:8080") == "example.com"
        assert extract_domain("http://localhost:3000/path") == "localhost"
    
    def test_extract_domain_without_scheme(self):
        """Test domain extraction from URL without scheme."""
        assert extract_domain("example.com") == "example.com"
        assert extract_domain("example.com/path") == "example.com"
    
    def test_domain_is_lowercased(self):
        """Test that extracted domain is lowercased."""
        assert extract_domain("https://EXAMPLE.COM") == "example.com"
        assert extract_domain("HTTP://ExAmPlE.CoM") == "example.com"
    
    def test_extract_domain_with_query_and_fragment(self):
        """Test domain extraction with query parameters and fragments."""
        assert extract_domain("https://example.com?q=1") == "example.com"
        assert extract_domain("https://example.com#section") == "example.com"
        assert extract_domain("https://example.com?q=1#section") == "example.com"


class TestValidateUrlForShortening:
    """Tests for validate_url_for_shortening function."""
    
    def test_valid_url(self):
        """Test that valid URL is normalized and returned."""
        result = validate_url_for_shortening("example.com")
        assert result == "https://example.com"
        
        result = validate_url_for_shortening("https://EXAMPLE.COM/Path/")
        assert result == "https://example.com/Path"
    
    def test_invalid_scheme(self):
        """Test that invalid scheme raises error."""
        with pytest.raises(ValidationError, match="Scheme 'ftp' is not allowed"):
            validate_url_for_shortening("ftp://example.com")
    
    def test_blocked_domain(self):
        """Test that blocked domain raises error."""
        with pytest.raises(ValidationError, match="Domain is blocked"):
            validate_url_for_shortening("localhost")
        
        with pytest.raises(ValidationError, match="Domain is blocked"):
            validate_url_for_shortening("https://example.com")
    
    def test_empty_url(self):
        """Test that empty URL raises error."""
        with pytest.raises(ValidationError, match="URL cannot be empty"):
            validate_url_for_shortening("")
    
    def test_url_with_all_components(self):
        """Test URL with all components is normalized correctly."""
        url = "HTTP://EXAMPLE.COM/Path/Sub/?a=1&b=2#Section"
        expected = "http://example.com/Path/Sub?a=1&b=2#Section"
        result = validate_url_for_shortening(url)
        assert result == expected


class TestValidationError:
    """Tests for ValidationError exception."""
    
    def test_error_message_format(self):
        """Test that error message is formatted correctly."""
        error = ValidationError("Test error", "http://example.com")
        assert str(error) == "Test error: http://example.com"
    
    def test_error_attributes(self):
        """Test that error attributes are set correctly."""
        error = ValidationError("Test error", "http://example.com")
        assert error.message == "Test error"
        assert error.url == "http://example.com"
    
    def test_error_is_value_error(self):
        """Test that ValidationError inherits from ValueError."""
        error = ValidationError("Test error", "http://example.com")
        assert isinstance(error, ValueError)
        assert isinstance(error, Exception)


class TestDefaultConstants:
    """Tests for default constants."""
    
    def test_default_allowed_schemes(self):
        """Test default allowed schemes."""
        assert DEFAULT_ALLOWED_SCHEMES == {"http", "https"}
    
    def test_default_blocked_domains(self):
        """Test default blocked domains."""
        assert "localhost" in DEFAULT_BLOCKED_DOMAINS
        assert "example.com" in DEFAULT_BLOCKED_DOMAINS
        assert "test.com" in DEFAULT_BLOCKED_DOMAINS
        assert "127.0.0.1" in DEFAULT_BLOCKED_DOMAINS