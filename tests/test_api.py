"""Unit tests for the main API facade.

These tests cover the URLShortener class and its main methods,
testing end-to-end flows and integration of all modules.
"""

import pytest

from pyshort.api import URLShortener
from pyshort.model import URL


class TestURLShortenerBasic:
    """Basic tests for URLShortener initialization and configuration."""

    def test_initialization_default(self):
        """Test initialization with default parameters."""
        shortener = URLShortener()
        assert shortener.storage.count() == 0
        assert shortener.stats.get_total_accesses() == 0

    def test_initialization_with_persistence(self):
        """Test initialization with file persistence paths."""
        shortener = URLShortener(
            persist_urls="/tmp/test_urls.json",
            persist_stats="/tmp/test_stats.json",
            code_length=8,
        )
        assert shortener.generator.code_length == 8


class TestShorten:
    """Tests for the shorten() method."""

    def test_shorten_valid_url(self):
        """Test shortening a valid URL."""
        shortener = URLShortener()
        short_code, url_obj = shortener.shorten("https://example.com/long/path")

        assert short_code is not None
        assert url_obj is not None
        assert url_obj.short_code == short_code
        assert url_obj.original_url == "https://example.com/long/path"
        assert len(short_code) == 6  # default length
        assert shortener.exists(short_code)

    def test_shorten_multiple_urls(self):
        """Test shortening multiple URLs and checking uniqueness."""
        shortener = URLShortener()
        urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
        ]

        short_codes = []
        for url in urls:
            short_code, _ = shortener.shorten(url)
            short_codes.append(short_code)

        # All short codes should be unique
        assert len(set(short_codes)) == 3
        # All should be valid
        for code in short_codes:
            assert shortener.exists(code)

    def test_shorten_with_custom_code_valid(self):
        """Test shortening with a valid custom code."""
        shortener = URLShortener()
        short_code, url_obj = shortener.shorten(
            "https://example.com", custom_code="mycode"
        )

        assert short_code == "mycode"
        assert url_obj.short_code == "mycode"
        assert url_obj.is_custom is True
        assert shortener.exists("mycode")

    def test_shorten_with_custom_code_duplicate(self):
        """Test that duplicate custom codes raise ValueError."""
        shortener = URLShortener()
        shortener.shorten("https://example.com/1", custom_code="mycode")

        with pytest.raises(ValueError, match="already exists"):
            shortener.shorten("https://example.com/2", custom_code="mycode")

    def test_shorten_with_custom_code_invalid(self):
        """Test that invalid custom codes raise ValueError."""
        shortener = URLShortener()

        with pytest.raises(ValueError, match="Invalid custom code"):
            shortener.shorten("https://example.com", custom_code="")

        with pytest.raises(ValueError, match="Invalid custom code"):
            shortener.shorten("https://example.com", custom_code="has spaces")

        with pytest.raises(ValueError, match="Invalid custom code"):
            shortener.shorten("https://example.com", custom_code="invalid!")

    def test_shorten_invalid_url(self):
        """Test that invalid URLs raise ValueError."""
        shortener = URLShortener()

        with pytest.raises(ValueError, match="Invalid URL"):
            shortener.shorten("")

        with pytest.raises(ValueError, match="Invalid URL"):
            shortener.shorten("not-a-url")

        with pytest.raises(ValueError, match="Invalid URL"):
            shortener.shorten("ftp://example.com")

    def test_shorten_various_valid_urls(self):
        """Test shortening various valid URL formats."""
        shortener = URLShortener()
        urls = [
            "http://example.com",
            "https://example.com",
            "https://sub.example.com/path",
            "https://example.com/path?query=value",
            "https://example.com/path#fragment",
            "https://example.com:8080/path",
        ]

        for url in urls:
            short_code, url_obj = shortener.shorten(url)
            assert short_code is not None
            assert url_obj.original_url == url


class TestResolve:
    """Tests for the resolve() method."""

    def test_resolve_existing_short_code(self):
        """Test resolving an existing short code."""
        shortener = URLShortener()
        original_url = "https://example.com/test"
        short_code, _ = shortener.shorten(original_url)

        resolved_url = shortener.resolve(short_code)

        assert resolved_url == original_url

    def test_resolve_nonexistent_short_code(self):
        """Test resolving a non-existent short code."""
        shortener = URLShortener()

        resolved_url = shortener.resolve("nonexistent")

        assert resolved_url is None

    def test_resolve_increments_access_count(self):
        """Test that resolving increments access count."""
        shortener = URLShortener()
        short_code, _ = shortener.shorten("https://example.com")

        # Initially, access count should be 0
        stats = shortener.get_stats(short_code)
        assert stats is not None
        assert stats["access_count"] == 0

        # Resolve once
        shortener.resolve(short_code)
        stats = shortener.get_stats(short_code)
        assert stats["access_count"] == 1

        # Resolve again
        shortener.resolve(short_code)
        stats = shortener.get_stats(short_code)
        assert stats["access_count"] == 2

    def test_resolve_tracks_access_history(self):
        """Test that resolving tracks access timestamps."""
        shortener = URLShortener()
        short_code, _ = shortener.shorten("https://example.com")

        # No access history initially
        stats = shortener.get_stats(short_code)
        assert stats is not None
        assert len(stats["access_history"]) == 0

        # Resolve multiple times
        shortener.resolve(short_code)
        shortener.resolve(short_code)
        shortener.resolve(short_code)

        stats = shortener.get_stats(short_code)
        assert len(stats["access_history"]) == 3


class TestGetStats:
    """Tests for the get_stats() method."""

    def test_get_stats_existing_short_code(self):
        """Test getting stats for an existing short code."""
        shortener = URLShortener()
        original_url = "https://example.com"
        short_code, url_obj = shortener.shorten(original_url)

        stats = shortener.get_stats(short_code)

        assert stats is not None
        assert stats["short_code"] == short_code
        assert stats["original_url"] == original_url
        assert stats["is_custom"] == False
        assert stats["access_count"] == 0
        assert len(stats["access_history"]) == 0
        assert "created_at" in stats

    def test_get_stats_with_access(self):
        """Test stats after resolving URL."""
        shortener = URLShortener()
        short_code, _ = shortener.shorten("https://example.com")

        # Access the URL
        shortener.resolve(short_code)
        shortener.resolve(short_code)

        stats = shortener.get_stats(short_code)

        assert stats is not None
        assert stats["access_count"] == 2
        assert len(stats["access_history"]) == 2

    def test_get_stats_custom_code(self):
        """Test stats for URL with custom code."""
        shortener = URLShortener()
        short_code, _ = shortener.shorten(
            "https://example.com", custom_code="custom"
        )

        stats = shortener.get_stats(short_code)

        assert stats is not None
        assert stats["is_custom"] is True

    def test_get_stats_nonexistent_short_code(self):
        """Test getting stats for non-existent short code."""
        shortener = URLShortener()

        stats = shortener.get_stats("nonexistent")

        assert stats is None


class TestDelete:
    """Tests for the delete() method."""

    def test_delete_existing_short_code(self):
        """Test deleting an existing short code."""
        shortener = URLShortener()
        short_code, _ = shortener.shorten("https://example.com")

        assert shortener.exists(short_code) is True

        result = shortener.delete(short_code)

        assert result is True
        assert shortener.exists(short_code) is False

    def test_delete_nonexistent_short_code(self):
        """Test deleting a non-existent short code."""
        shortener = URLShortener()

        result = shortener.delete("nonexistent")

        assert result is False

    def test_delete_removes_statistics(self):
        """Test that deleting also removes statistics."""
        shortener = URLShortener()
        short_code, _ = shortener.shorten("https://example.com")

        # Access the URL
        shortener.resolve(short_code)
        shortener.resolve(short_code)

        # Verify stats exist
        stats = shortener.get_stats(short_code)
        assert stats is not None
        assert stats["access_count"] == 2

        # Delete the URL
        shortener.delete(short_code)

        # Stats should be gone
        stats = shortener.get_stats(short_code)
        assert stats is None

    def test_delete_custom_code(self):
        """Test deleting a URL with custom code."""
        shortener = URLShortener()
        shortener.shorten("https://example.com", custom_code="mycode")

        assert shortener.exists("mycode") is True

        result = shortener.delete("mycode")

        assert result is True
        assert shortener.exists("mycode") is False


class TestIntegration:
    """Integration tests for end-to-end workflows."""

    def test_full_workflow_shorten_resolve_delete(self, tmp_path):
        """Test complete workflow: shorten, resolve, stats, delete."""
        shortener = URLShortener(
            persist_urls=str(tmp_path / "urls.json"),
            persist_stats=str(tmp_path / "stats.json"),
        )

        # 1. Shorten a URL
        short_code, url_obj = shortener.shorten(
            "https://example.com/some/long/path"
        )
        assert short_code is not None
        assert shortener.exists(short_code)

        # 2. Resolve it multiple times
        for _ in range(5):
            resolved = shortener.resolve(short_code)
            assert resolved == "https://example.com/some/long/path"

        # 3. Check stats
        stats = shortener.get_stats(short_code)
        assert stats is not None
        assert stats["access_count"] == 5
        assert len(stats["access_history"]) == 5

        # 4. Delete it
        result = shortener.delete(short_code)
        assert result is True
        assert shortener.exists(short_code) is False

        # 5. Verify deletion
        assert shortener.resolve(short_code) is None
        assert shortener.get_stats(short_code) is None

    def test_multiple_urls_workflow(self):
        """Test workflow with multiple URLs."""
        shortener = URLShortener()

        # Create multiple URLs
        mappings = {
            "url1": "https://example.com/1",
            "url2": "https://example.com/2",
            "url3": "https://example.com/3",
        }

        for name, url in mappings.items():
            shortener.shorten(url, custom_code=name)

        # Verify all exist
        for name in mappings:
            assert shortener.exists(name)

        # Access them different number of times
        shortener.resolve("url1")
        shortener.resolve("url1")
        shortener.resolve("url2")

        # Check stats
        stats1 = shortener.get_stats("url1")
        stats2 = shortener.get_stats("url2")
        stats3 = shortener.get_stats("url3")

        assert stats1["access_count"] == 2
        assert stats2["access_count"] == 1
        assert stats3["access_count"] == 0

        # Delete one
        shortener.delete("url2")
        assert shortener.exists("url2") is False
        assert shortener.exists("url1") is True
        assert shortener.exists("url3") is True

    def test_global_stats_workflow(self):
        """Test global statistics across multiple URLs."""
        shortener = URLShortener()

        # Create URLs with different access patterns
        codes = []
        for i in range(5):
            short_code, _ = shortener.shorten(f"https://example.com/{i}")
            codes.append(short_code)

        # Access them
        for code in codes:
            for _ in range(codes.index(code) + 1):
                shortener.resolve(code)

        # Check global stats
        global_stats = shortener.get_global_stats()

        assert global_stats["total_urls"] == 5
        # Total accesses: 1 + 2 + 3 + 4 + 5 = 15
        assert global_stats["total_accesses"] == 15
        assert global_stats["urls_with_accesses"] == 5

    def test_error_handling_workflow(self):
        """Test error handling throughout the workflow."""
        shortener = URLShortener()

        # Invalid URL
        with pytest.raises(ValueError):
            shortener.shorten("not-a-url")

        # Invalid custom code
        with pytest.raises(ValueError):
            shortener.shorten("https://example.com", custom_code="has space")

        # Duplicate custom code
        shortener.shorten("https://example.com/1", custom_code="code1")
        with pytest.raises(ValueError):
            shortener.shorten("https://example.com/2", custom_code="code1")

        # Resolve non-existent
        assert shortener.resolve("nonexistent") is None

        # Get stats for non-existent
        assert shortener.get_stats("nonexistent") is None

        # Delete non-existent
        assert shortener.delete("nonexistent") is False

    def test_clear_workflow(self):
        """Test clearing all data."""
        shortener = URLShortener()

        # Create and access some URLs
        for i in range(3):
            short_code, _ = shortener.shorten(f"https://example.com/{i}")
            for _ in range(2):
                shortener.resolve(short_code)

        # Verify data exists
        assert shortener.storage.count() == 3
        assert shortener.stats.get_total_accesses() == 6

        # Clear all
        shortener.clear()

        # Verify everything is cleared
        assert shortener.storage.count() == 0
        assert shortener.stats.get_total_accesses() == 0
        assert len(shortener.generator._generated_codes) == 0


class TestHelperMethods:
    """Tests for helper methods."""

    def test_exists(self):
        """Test the exists() helper method."""
        shortener = URLShortener()

        assert shortener.exists("nonexistent") is False

        short_code, _ = shortener.shorten("https://example.com")
        assert shortener.exists(short_code) is True

        shortener.delete(short_code)
        assert shortener.exists(short_code) is False

    def test_get_url_info(self):
        """Test the get_url_info() helper method."""
        shortener = URLShortener()
        original_url = "https://example.com"
        short_code, url_obj = shortener.shorten(original_url)

        info = shortener.get_url_info(short_code)

        assert info is not None
        assert info["short_code"] == short_code
        assert info["original_url"] == original_url
        assert info["is_custom"] is False
        assert "created_at" in info

    def test_get_url_info_nonexistent(self):
        """Test get_url_info for non-existent short code."""
        shortener = URLShortener()

        info = shortener.get_url_info("nonexistent")

        assert info is None

    def test_get_all_urls(self):
        """Test getting all URLs."""
        shortener = URLShortener()

        # Create multiple URLs
        for i in range(3):
            shortener.shorten(f"https://example.com/{i}")

        all_urls = shortener.get_all_urls()

        assert len(all_urls) == 3
        assert all("short_code" in url for url in all_urls)
        assert all("original_url" in url for url in all_urls)

    def test_get_all_urls_empty(self):
        """Test getting all URLs when storage is empty."""
        shortener = URLShortener()

        all_urls = shortener.get_all_urls()

        assert all_urls == []