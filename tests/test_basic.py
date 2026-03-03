"""Basic tests for PyShort URL shortener."""

import pytest
from pyshort import URLShortener


def test_shorten_and_resolve():
    """Test URL shortening and resolution."""
    shortener = URLShortener()
    
    # Test basic shortening
    original_url = "https://example.com"
    short_code = shortener.shorten(original_url)
    
    assert short_code is not None
    assert len(short_code) == 6  # default length
    
    # Test resolution
    resolved_url = shortener.resolve(short_code)
    assert resolved_url == original_url
    
    # Test that accessing increments stats
    stats = shortener.get_stats(short_code)
    assert stats is not None
    assert stats["access_count"] == 1
    assert stats["original_url"] == original_url


def test_custom_code():
    """Test using custom short codes."""
    shortener = URLShortener()
    
    original_url = "https://example.com/custom"
    custom_code = "mylink"
    short_code = shortener.shorten(original_url, custom_code=custom_code)
    
    assert short_code == custom_code
    
    resolved_url = shortener.resolve(short_code)
    assert resolved_url == original_url


def test_duplicate_custom_code():
    """Test that duplicate custom codes are rejected."""
    shortener = URLShortener()
    
    original_url1 = "https://example.com/first"
    original_url2 = "https://example.com/second"
    custom_code = "duplicate"
    
    shortener.shorten(original_url1, custom_code=custom_code)
    
    with pytest.raises(ValueError, match="already in use"):
        shortener.shorten(original_url2, custom_code=custom_code)


def test_invalid_url():
    """Test that invalid URLs are rejected."""
    shortener = URLShortener()
    
    invalid_urls = [
        "not-a-url",
        "htp://invalid-scheme.com",
        "",
        "www.example.com",  # Missing scheme
        "javascript:alert('xss')",
    ]
    
    for invalid_url in invalid_urls:
        with pytest.raises(ValueError, match="Invalid URL"):
            shortener.shorten(invalid_url)


def test_invalid_custom_code():
    """Test that invalid custom codes are rejected."""
    shortener = URLShortener()
    
    invalid_codes = [
        "ab",  # Too short
        "a" * 25,  # Too long
        "test space",  # Contains space
        "test/code",  # Contains slash
        "api",  # Reserved word
        "12345",  # All numbers
    ]
    
    for invalid_code in invalid_codes:
        url = "https://example.com"
        with pytest.raises(ValueError):
            shortener.shorten(url, custom_code=invalid_code)


def test_delete():
    """Test URL deletion."""
    shortener = URLShortener()
    
    original_url = "https://example.com/delete-me"
    short_code = shortener.shorten(original_url)
    
    # Should exist before deletion
    assert shortener.exists(short_code) is True
    
    # Delete the URL
    result = shortener.delete(short_code)
    assert result is True
    
    # Should not exist after deletion
    assert shortener.exists(short_code) is False
    
    # Resolving should return None
    resolved = shortener.resolve(short_code)
    assert resolved is None


def test_delete_nonexistent():
    """Test deleting a non-existent short code."""
    shortener = URLShortener()
    
    result = shortener.delete("nonexistent")
    assert result is False


def test_multiple_accesses():
    """Test that multiple accesses are tracked correctly."""
    shortener = URLShortener()
    
    original_url = "https://example.com/multiple"
    short_code = shortener.shorten(original_url)
    
    # Access the URL multiple times
    for _ in range(5):
        shortener.resolve(short_code)
    
    stats = shortener.get_stats(short_code)
    assert stats["access_count"] == 5
    
    # Check recent accesses
    assert len(stats["recent_accesses"]) == 10  # Last 10, should have 5


def test_get_url_info():
    """Test getting URL info without recording access."""
    shortener = URLShortener()
    
    original_url = "https://example.com/info"
    short_code = shortener.shorten(original_url)
    
    # Get info without recording access
    info = shortener.get_url_info(short_code)
    assert info is not None
    assert info["original_url"] == original_url
    assert info["short_code"] == short_code
    assert "created_at" in info
    
    # Stats should not have been incremented
    stats = shortener.get_stats(short_code)
    assert stats["access_count"] == 0


def test_get_all_urls():
    """Test getting all URLs."""
    shortener = URLShortener()
    
    urls = [
        "https://example.com/1",
        "https://example.com/2",
        "https://example.com/3",
    ]
    
    short_codes = []
    for url in urls:
        code = shortener.shorten(url)
        short_codes.append(code)
    
    all_urls = shortener.get_all_urls()
    assert len(all_urls) == 3
    
    for code in short_codes:
        assert code in all_urls


def test_get_global_stats():
    """Test global statistics."""
    shortener = URLShortener()
    
    # Create some URLs
    url1 = "https://example.com/popular"
    url2 = "https://example.com/unpopular"
    
    code1 = shortener.shorten(url1)
    code2 = shortener.shorten(url2)
    
    # Access the first URL many times
    for _ in range(10):
        shortener.resolve(code1)
    
    # Access the second URL once
    shortener.resolve(code2)
    
    stats = shortener.get_global_stats()
    assert stats["total_urls"] == 2
    assert stats["total_accesses"] == 11
    
    # Check most accessed
    most_accessed = stats["most_accessed"]
    assert len(most_accessed) == 2
    assert most_accessed[0][0] == code1  # code1 should be first
    assert most_accessed[0][1] == 10
    assert most_accessed[1][0] == code2
    assert most_accessed[1][1] == 1


def test_clear():
    """Test clearing all data."""
    shortener = URLShortener()
    
    # Create some URLs
    shortener.shorten("https://example.com/1")
    shortener.shorten("https://example.com/2")
    
    # Clear everything
    shortener.clear()
    
    # Should be empty
    assert shortener.get_global_stats()["total_urls"] == 0
    assert shortener.get_global_stats()["total_accesses"] == 0


def test_generate_different_codes():
    """Test that multiple shorten calls generate different codes."""
    shortener = URLShortener()
    
    urls = [f"https://example.com/{i}" for i in range(10)]
    short_codes = [shortener.shorten(url) for url in urls]
    
    # All codes should be unique
    assert len(set(short_codes)) == 10