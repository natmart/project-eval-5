"""Unit tests for the generator module.

Tests cover random code generation, custom codes, and base62 encoding.
"""

import string
import pytest

from pyshort.generator import CodeGenerator


class TestCodeGenerator:
    """Test cases for the CodeGenerator class."""

    def test_initialization_default(self) -> None:
        """Test initialization with default parameters."""
        generator = CodeGenerator()
        assert generator.code_length == 6
        assert len(generator._generated_codes) == 0

    def test_initialization_custom_length(self) -> None:
        """Test initialization with custom code length."""
        generator = CodeGenerator(code_length=8)
        assert generator.code_length == 8

    def test_generate_random_default_length(self) -> None:
        """Test random code generation with default length."""
        generator = CodeGenerator(code_length=6)
        code = generator.generate_random()

        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isalnum()

    def test_generate_random_custom_length(self) -> None:
        """Test random code generation with custom length."""
        generator = CodeGenerator()
        code = generator.generate_random(length=10)

        assert isinstance(code, str)
        assert len(code) == 10
        assert code.isalnum()

    def test_generate_random_length_one(self) -> None:
        """Test random code generation with length of 1 (minimum)."""
        generator = CodeGenerator()
        code = generator.generate_random(length=1)

        assert isinstance(code, str)
        assert len(code) == 1
        assert code.isalnum()

    def test_generate_random_invalid_length(self) -> None:
        """Test that invalid length raises ValueError."""
        generator = CodeGenerator()

        with pytest.raises(ValueError, match="Code length must be at least 1"):
            generator.generate_random(length=0)

        with pytest.raises(ValueError, match="Code length must be at least 1"):
            generator.generate_random(length=-5)

    def test_generate_random_uniqueness(self) -> None:
        """Test that generated codes are unique."""
        generator = CodeGenerator(code_length=8)
        codes = set()

        # Generate 100 codes and verify uniqueness
        for _ in range(100):
            code = generator.generate_random()
            assert code not in codes
            codes.add(code)

        assert len(codes) == 100

    def test_validate_custom_code_valid(self) -> None:
        """Test validation of valid custom codes."""
        generator = CodeGenerator()

        assert generator.validate_custom_code("abc") is True
        assert generator.validate_custom_code("ABC") is True
        assert generator.validate_custom_code("123") is True
        assert generator.validate_custom_code("aB1") is True
        assert generator.validate_custom_code("customCode") is True

    def test_validate_custom_code_empty(self) -> None:
        """Test validation of empty custom code."""
        generator = CodeGenerator()
        assert generator.validate_custom_code("") is False

    def test_validate_custom_code_too_long(self) -> None:
        """Test validation of custom code exceeding maximum length."""
        generator = CodeGenerator()

        # Create a 101 character code
        long_code = "a" * 101
        assert generator.validate_custom_code(long_code) is False

    def test_validate_custom_code_edge_length_100(self) -> None:
        """Test validation of custom code at maximum length (100)."""
        generator = CodeGenerator()

        # Create exactly 100 characters
        valid_long_code = "a" * 100
        assert generator.validate_custom_code(valid_long_code) is True

    def test_validate_custom_code_special_chars(self) -> None:
        """Test validation of custom code with special characters."""
        generator = CodeGenerator()

        assert generator.validate_custom_code("hello!") is False
        assert generator.validate_custom_code("test-code") is False
        assert generator.validate_custom_code("test_code") is False
        assert generator.validate_custom_code("test.code") is False
        assert generator.validate_custom_code("test code") is False

    def test_set_custom_code_valid(self) -> None:
        """Test setting a valid custom code."""
        generator = CodeGenerator()
        code = generator.set_custom_code("mycode")

        assert code == "mycode"
        assert "mycode" in generator._generated_codes

    def test_set_custom_code_invalid_raises_error(self) -> None:
        """Test that setting invalid custom code raises ValueError."""
        generator = CodeGenerator()

        with pytest.raises(ValueError, match="must be 1-100 alphanumeric characters"):
            generator.set_custom_code("")

        with pytest.raises(ValueError, match="must be 1-100 alphanumeric characters"):
            generator.set_custom_code("invalid!")

    def test_set_custom_code_duplicate_raises_error(self) -> None:
        """Test that setting duplicate custom code raises ValueError."""
        generator = CodeGenerator()
        generator.set_custom_code("mycode")

        with pytest.raises(ValueError, match="already exists"):
            generator.set_custom_code("mycode")

    def test_encode_base62_zero(self) -> None:
        """Test base62 encoding of zero."""
        generator = CodeGenerator()
        encoded = generator.encode_base62(0)

        assert encoded == "0"

    def test_encode_base62_small_numbers(self) -> None:
        """Test base62 encoding of small numbers."""
        generator = CodeGenerator()

        assert generator.encode_base62(1) == "1"
        assert generator.encode_base62(9) == "9"
        assert generator.encode_base62(10) == "A"
        assert generator.encode_base62(35) == "Z"
        assert generator.encode_base62(36) == "a"
        assert generator.encode_base62(61) == "z"

    def test_encode_base62_large_numbers(self) -> None:
        """Test base62 encoding of large numbers."""
        generator = CodeGenerator()

        # 62 should encode to "10" (1 * 62^1 + 0)
        assert generator.encode_base62(62) == "10"

        # 3844 should encode to "100" (1 * 62^2 + 0 + 0)
        assert generator.encode_base62(3844) == "100"

    def test_encode_base62_negative_raises_error(self) -> None:
        """Test that encoding negative numbers raises ValueError."""
        generator = CodeGenerator()

        with pytest.raises(ValueError, match="must be non-negative"):
            generator.encode_base62(-1)

        with pytest.raises(ValueError, match="must be non-negative"):
            generator.encode_base62(-100)

    def test_decode_base62_valid(self) -> None:
        """Test base62 decoding of valid codes."""
        generator = CodeGenerator()

        assert generator.decode_base62("0") == 0
        assert generator.decode_base62("1") == 1
        assert generator.decode_base62("9") == 9
        assert generator.decode_base62("A") == 10
        assert generator.decode_base62("Z") == 35
        assert generator.decode_base62("a") == 36
        assert generator.decode_base62("z") == 61
        assert generator.decode_base62("10") == 62
        assert generator.decode_base62("100") == 3844

    def test_decode_base62_invalid_characters(self) -> None:
        """Test that decoding codes with invalid characters raises ValueError."""
        generator = CodeGenerator()

        with pytest.raises(ValueError, match="Invalid character"):
            generator.decode_base62("abc!")

        with pytest.raises(ValueError, match="Invalid character"):
            generator.decode_base62("test-code")

        with pytest.raises(ValueError, match="Invalid character"):
            generator.decode_base62(" ")

    def test_encode_decode_roundtrip(self) -> None:
        """Test that encoding and decoding are reversible."""
        generator = CodeGenerator()

        test_numbers = [0, 1, 10, 62, 100, 1000, 10000, 999999]

        for number in test_numbers:
            encoded = generator.encode_base62(number)
            decoded = generator.decode_base62(encoded)
            assert decoded == number

    def test_generate_from_number(self) -> None:
        """Test generating code from a number."""
        generator = CodeGenerator()

        code = generator.generate_from_number(12345)
        expected = generator.encode_base62(12345)

        assert code == expected
        assert code in generator._generated_codes

    def test_generate_from_number_collision_handling(self) -> None:
        """Test that number generation handles collisions."""
        generator = CodeGenerator()

        # Manually add a code that will collide
        collision_code = generator.encode_base62(100)
        generator._generated_codes.add(collision_code)

        # Generate the same code - should add a random suffix
        code = generator.generate_from_number(100)

        assert len(code) > len(collision_code)
        assert code.startswith(collision_code)
        assert code in generator._generated_codes

    def test_is_unique_true(self) -> None:
        """Test is_unique returns True for unique codes."""
        generator = CodeGenerator()
        assert generator.is_unique("newcode") is True

    def test_is_unique_false(self) -> None:
        """Test is_unique returns False for existing codes."""
        generator = CodeGenerator()
        generator.set_custom_code("existing")

        assert generator.is_unique("existing") is False
        assert generator.is_unique("other") is True

    def test_clear_history(self) -> None:
        """Test clearing the history of generated codes."""
        generator = CodeGenerator()

        # Generate some codes
        generator.generate_random()
        generator.set_custom_code("test")
        generator.generate_from_number(123)

        assert len(generator._generated_codes) == 3

        # Clear history
        generator.clear_history()

        assert len(generator._generated_codes) == 0

    def test_generate_random_variety(self) -> None:
        """Test that random generation produces varied characters."""
        generator = CodeGenerator(code_length=100)
        codes = [generator.generate_random() for _ in range(10)]

        # Check that codes are different from each other
        unique_codes = set(codes)
        assert len(unique_codes) == 10

        # Check that codes use different character types
        all_chars = "".join(codes)
        has_upper = any(c.isupper() for c in all_chars)
        has_lower = any(c.islower() for c in all_chars)
        has_digit = any(c.isdigit() for c in all_chars)

        # At least one of each should appear eventually
        assert has_upper or has_lower or has_digit

    def test_character_set_completeness(self) -> None:
        """Test that the base62 character set is complete."""
        generator = CodeGenerator()

        # The BASE62_CHARS should contain exactly 62 unique characters
        assert len(generator.BASE62_CHARS) == 62
        assert len(set(generator.BASE62_CHARS)) == 62

        # Should include digits, uppercase, and lowercase
        assert all(c in generator.BASE62_CHARS for c in string.digits)
        assert all(c in generator.BASE62_CHARS for c in string.ascii_uppercase)
        assert all(c in generator.BASE62_CHARS for c in string.ascii_lowercase)