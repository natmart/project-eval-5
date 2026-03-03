"""Integration tests for complete URL shortener workflows.

These tests demonstrate end-to-end functionality across all components,
validating that the entire system works together correctly.
"""

import pytest

from pyshort import URLShortener


class TestCompleteWorkflow:
    """Test complete URL shortener lifecycle from creation to deletion."""

    def test_shorten_resolve_delete_workflow(self):
        """Test the complete workflow: shorten, resolve, and delete."""
        shortener = URLShortener()

        # Step 1: Shorten a URL
        original_url = "https://example.com/very/long/path"
        short_code = shortener.shorten(original_url)
        
        assert isinstance(short_code, str)
        assert len(short_code) > 0
        assert shortener.exists(short_code) is True

        # Step 2: Resolve the short code
        resolved_url = shortener.resolve(short_code)
        assert resolved_url == original_url

        # Step 3: Verify URL info
        url_info = shortener.get_url_info(short_code)
        assert url_info["code"] == short_code
        assert url_info["url"] == original_url

        # Step 4: Delete the URL
        deleted = shortener.delete(short_code)
        assert deleted is True
        
        # Step 5: Verify deletion
        assert shortener.exists(short_code) is False
        with pytest.raises(KeyError, match="not found"):
            shortener.resolve(short_code)

    def test_multiple_resolves_workflow(self):
        """Test resolving the same short code multiple times."""
        shortener = URLShortener()

        original_url = "https://github.com/example/repo"
        short_code = shortener.shorten(original_url)

        # Resolve multiple times
        for _ in range(5):
            resolved = shortener.resolve(short_code)
            assert resolved == original_url

        # Verify URL still exists and returns correct info
        url_info = shortener.get_url_info(short_code)
        assert url_info["url"] == original_url

    def test_multiple_urls_workflow(self):
        """Test workflow with multiple URLs being shortened and managed."""
        shortener = URLShortener()

        urls = [
            "https://first.example.com/path",
            "https://second.example.org/another/path",
            "https://third.example.net/yet/another/path",
        ]

        # Shorten all URLs
        short_codes = []
        for url in urls:
            code = shortener.shorten(url)
            short_codes.append(code)
            assert shortener.exists(code) is True

        # Verify all codes are unique
        assert len(set(short_codes)) == len(short_codes)

        # Resolve all URLs and verify correctness
        for code, original_url in zip(short_codes, urls):
            resolved = shortener.resolve(code)
            assert resolved == original_url

        # Get all URLs
        all_urls = shortener.get_all_urls()
        assert len(all_urls) == 3
        
        # Verify all URLs are present
        all_url_codes = {item["code"] for item in all_urls}
        assert all_url_codes == set(short_codes)

        # Delete one URL
        deleted = shortener.delete(short_codes[0])
        assert deleted is True
        assert len(shortener.get_all_urls()) == 2

        # Clean up remaining URLs
        for code in short_codes[1:]:
            shortener.delete(code)
        assert len(shortener.get_all_urls()) == 0

    def test_custom_code_workflow(self):
        """Test complete workflow with custom short codes."""
        shortener = URLShortener()

        # Shorten with custom code
        original_url = "https://docs.example.com/api"
        custom_code = "mydocs"
        returned_code = shortener.shorten(original_url, custom_code=custom_code)

        assert returned_code == custom_code
        assert shortener.exists(custom_code) is True

        # Resolve using custom code
        resolved = shortener.resolve(custom_code)
        assert resolved == original_url

        # Verify info
        url_info = shortener.get_url_info(custom_code)
        assert url_info["code"] == custom_code
        assert url_info["url"] == original_url

        # Delete
        deleted = shortener.delete(custom_code)
        assert deleted is True
        assert shortener.exists(custom_code) is False

    def test_custom_code_collision_workflow(self):
        """Test workflow handling duplicate custom codes."""
        shortener = URLShortener()

        url1 = "https://example.com/first"
        url2 = "https://example.com/second"
        custom_code = "shared"

        # First shortening with custom code should succeed
        code1 = shortener.shorten(url1, custom_code=custom_code)
        assert code1 == custom_code

        # Second attempt with same custom code should fail
        with pytest.raises(ValueError, match="already exists"):
            shortener.shorten(url2, custom_code=custom_code)

        # Verify first URL is still accessible
        resolved = shortener.resolve(custom_code)
        assert resolved == url1

    def test_empty_state_workflow(self):
        """Test workflow starting with empty shortener state."""
        shortener = URLShortener()

        # Verify initial state is empty
        assert shortener.get_all_urls() == []

        # Try to resolve non-existent code
        with pytest.raises(KeyError, match="not found"):
            shortener.resolve("nonexistent")

        # Try to get info for non-existent code
        with pytest.raises(KeyError, match="not found"):
            shortener.get_url_info("nonexistent")

        # Delete non-existent code should return False
        result = shortener.delete("nonexistent")
        assert result is False

        # After adding a URL, operations should work
        url = "https://example.com"
        code = shortener.shorten(url)
        assert len(shortener.get_all_urls()) == 1
        assert shortener.resolve(code) == url

    def test_clear_workflow(self):
        """Test workflow including clearing all URLs."""
        shortener = URLShortener()

        # Add multiple URLs
        urls = ["https://a.example.com", "https://b.example.com", "https://c.example.com"]
        codes = [shortener.shorten(url) for url in urls]

        # Verify all are present
        assert len(shortener.get_all_urls()) == 3
        for code in codes:
            assert shortener.exists(code) is True

        # Clear all URLs
        shortener.clear()

        # Verify all are gone
        assert len(shortener.get_all_urls()) == 0
        for code in codes:
            assert shortener.exists(code) is False

    def test_url_variations_workflow(self):
        """Test workflow with various URL formats."""
        shortener = URLShortener()

        # Test various URL formats
        test_urls = [
            "https://example.com",
            "http://example.org",
            "https://example.com:8080/path",
            "https://example.com/path?query=value",
            "https://example.com/path?param1=one&param2=two",
            "https://subdomain.example.com/path",
            "https://example.com/very/long/path/with/many/segments",
        ]

        for url in test_urls:
            code = shortener.shorten(url)
            resolved = shortener.resolve(code)
            assert resolved == url
            shortener.delete(code)

        # Final state should be clean
        assert len(shortener.get_all_urls()) == 0

    def test_error_handling_workflow(self):
        """Test workflow with various error conditions."""
        shortener = URLShortener()

        # Test invalid URL (empty string)
        with pytest.raises(ValueError, match="non-empty"):
            shortener.shorten("")

        # Test invalid URL (None)
        with pytest.raises(ValueError, match="non-empty"):
            shortener.shorten(None)

        # Resolve non-existent code
        with pytest.raises(KeyError, match="not found"):
            shortener.resolve("doesnotexist")

        # Get info for non-existent code
        with pytest.raises(KeyError, match="not found"):
            shortener.get_url_info("doesnotexist")

        # Invalid custom code (special characters)
        with pytest.raises(ValueError, match="alphanumeric"):
            shortener.shorten("https://example.com", custom_code="bad-code!")


class TestMultipleInstances:
    """Test behavior with multiple URLShortener instances."""

    def test_independent_instances(self):
        """Test that multiple instances work independently."""
        shortener1 = URLShortener()
        shortener2 = URLShortener()

        # Add URL to first instance
        code1 = shortener1.shorten("https://first.example.com")
        
        # Add URL to second instance
        code2 = shortener2.shorten("https://second.example.com")

        # Verify isolation
        assert shortener1.exists(code1) is True
        assert shortener1.exists(code2) is False
        assert shortener2.exists(code1) is False
        assert shortener2.exists(code2) is True

        # Verify resolutions are independent
        assert shortener1.resolve(code1) == "https://first.example.com"
        assert shortener2.resolve(code2) == "https://second.example.com"

        # Deleting from one doesn't affect the other
        shortener1.delete(code1)
        assert shortener1.exists(code1) is False
        assert shortener2.exists(code2) is True


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_mixed_random_and_custom_codes(self):
        """Test workflow with mix of random and custom codes."""
        shortener = URLShortener()

        # Add URLs with custom codes
        custom_pairs = [
            ("https://google.com", "google"),
            ("https://github.com", "github"),
        ]
        for url, code in custom_pairs:
            shortener.shorten(url, custom_code=code)

        # Add URLs with random codes
        random_urls = [
            "https://random1.example.com",
            "https://random2.example.com",
            "https://random3.example.com",
        ]
        random_codes = [shortener.shorten(url) for url in random_urls]

        # Verify all codes exist and resolve correctly
        for url, code in custom_pairs:
            assert shortener.resolve(code) == url

        for code, url in zip(random_codes, random_urls):
            assert shortener.resolve(code) == url

        # Total count should be correct
        all_urls = shortener.get_all_urls()
        assert len(all_urls) == 5

        # Clean up
        shortener.clear()
        assert len(shortener.get_all_urls()) == 0

    def test_crud_operations_sequence(self):
        """Test a complete CRUD (Create-Read-Update-Delete) sequence."""
        shortener = URLShortener()

        # Create
        url = "https://example.com/original"
        code = shortener.shorten(url)
        assert shortener.exists(code) is True

        # Read (verify)
        assert shortener.resolve(code) == url
        info = shortener.get_url_info(code)
        assert info["url"] == url

        # List (read all)
        all_urls = shortener.get_all_urls()
        assert len(all_urls) == 1
        assert all_urls[0]["code"] == code

        # Delete
        deleted = shortener.delete(code)
        assert deleted is True

        # Verify deletion
        assert shortener.exists(code) is False
        assert len(shortener.get_all_urls()) == 0

    def test_batch_operations_workflow(self):
        """Test workflow simulating batch URL processing."""
        shortener = URLShortener()

        # Batch create - simulate processing many URLs
        num_urls = 10
        test_data = [
            f"https://example.com/page/{i}" for i in range(num_urls)
        ]
        
        codes = []
        for url in test_data:
            code = shortener.shorten(url)
            codes.append(code)

        # Verify all were created
        assert len(shortener.get_all_urls()) == num_urls

        # Batch resolve - simulating access tracking
        resolutions = []
        for code in codes:
            url = shortener.resolve(code)
            resolutions.append(url)

        # Verify all resolutions match original URLs
        assert resolutions == test_data

        # Batch delete
        deleted_count = 0
        for code in codes:
            if shortener.delete(code):
                deleted_count += 1

        assert deleted_count == num_urls
        assert len(shortener.get_all_urls()) == 0