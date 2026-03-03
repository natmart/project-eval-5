"""Tests for the short code generator module."""

import pytest
from pyshort.generator import (
    ShortCodeGenerator,
    encode_base62,
    decode_base62,
    generate_random_code,
    validate_custom_code,
)


class TestShortCodeGenerator:
    """Test cases for ShortCodeGenerator class."""
    
    def test_init_default(self):
        """Test generator initialization with default parameters."""
        generator = ShortCodeGenerator()
        assert generator.code_length == 6
        assert generator.existing_codes == set()
        assert generator.is_unique_callback is None
    
    def test_init_with_length(self):
        """Test generator initialization with custom length."""
        generator = ShortCodeGenerator(code_length=10)
        assert generator.code_length == 10
    
    def test_init_with_existing_codes(self):
        """Test generator initialization with existing codes."""
        existing = {"abc123", "xyz789"}
        generator = ShortCodeGenerator(existing_codes=existing)
        assert generator.existing_codes == existing
    
    def test_init_with_callback(self):
        """Test generator initialization with uniqueness callback."""
        callback = lambda x: True
        generator = ShortCodeGenerator(is_unique_callback=callback)
        assert generator.is_unique_callback is callback
    
    def test_init_invalid_length(self):
        """Test that invalid length raises ValueError."""
        with pytest.raises(ValueError, match="code_length must be at least 1"):
            ShortCodeGenerator(code_length=0)
        with pytest.raises(ValueError, match="code_length must be at least 1"):
            ShortCodeGenerator(code_length=-5)
    
    def test_generate_random_code(self):
        """Test random code generation."""
        generator = ShortCodeGenerator(code_length=6)
        code = generator.generate_random_code()
        assert len(code) == 6
        assert code.isalnum()
    
    def test_generate_random_code_custom_length(self):
        """Test random code generation with custom length."""
        generator = ShortCodeGenerator(code_length=10)
        code = generator.generate_random_code()
        assert len(code) == 10
        assert code.isalnum()
    
    def test_generate_random_code_uniqueness(self):
        """Test that generated codes are unique."""
        generator = ShortCodeGenerator(code_length=6)
        codes = {generator.generate_random_code() for _ in range(100)}
        assert len(codes) == 100
    
    def test_generate_random_code_avoids_existing(self):
        """Test that generated codes avoid existing codes."""
        existing_codes = {"abc123", "xyz789"}
        generator = ShortCodeGenerator(code_length=6, existing_codes=existing_codes)
        for _ in range(50):
            code = generator.generate_random_code()
            assert code not in existing_codes
    
    def test_generate_random_code_with_callback(self):
        """Test random code generation with uniqueness callback."""
        used_codes = set()
        
        def callback(code):
            return code not in used_codes
        
        generator = ShortCodeGenerator(code_length=6, is_unique_callback=callback)
        code1 = generator.generate_random_code()
        
        # Mark code as used
        used_codes.add(code1)
        code2 = generator.generate_random_code()
        
        assert code1 != code2
        assert code2 not in used_codes
    
    def test_generate_random_code_max_attempts(self):
        """Test that max attempts limit works."""
        existing_codes = {"aaaaaaaa"}  # Only valid code of length 8
        
        def always_false(code):
            return False
        
        generator = ShortCodeGenerator(
            code_length=8,
            existing_codes=existing_codes,
            is_unique_callback=always_false,
        )
        with pytest.raises(RuntimeError, match="Failed to generate unique code"):
            generator.generate_random_code(max_attempts=10)
    
    def test_validate_custom_code_valid(self):
        """Test validation of valid custom codes."""
        generator = ShortCodeGenerator()
        assert generator.validate_custom_code("abc123") is True
        assert generator.validate_custom_code("XYZ789") is True
        assert generator.validate_custom_code("AbCdEf") is True
    
    def test_validate_custom_code_empty(self):
        """Test validation of empty code."""
        generator = ShortCodeGenerator()
        assert generator.validate_custom_code("") is False
    
    def test_validate_custom_code_special_chars(self):
        """Test validation of codes with special characters."""
        generator = ShortCodeGenerator()
        assert generator.validate_custom_code("abc-123") is False
        assert generator.validate_custom_code("abc_123") is False
        assert generator.validate_custom_code("abc.123") is False
        assert generator.validate_custom_code("abc 123") is False
    
    def test_validate_custom_code_uniqueness(self):
        """Test that validation checks uniqueness."""
        existing_codes = {"abc123", "xyz789"}
        generator = ShortCodeGenerator(existing_codes=existing_codes)
        
        assert generator.validate_custom_code("abc123") is False
        assert generator.validate_custom_code("xyz789") is False
        assert generator.validate_custom_code("newcode") is True
    
    def test_accept_custom_code_valid(self):
        """Test accepting a valid custom code."""
        generator = ShortCodeGenerator()
        code = generator.accept_custom_code("mycode123")
        assert code == "mycode123"
        assert code in generator.existing_codes
    
    def test_accept_custom_code_invalid(self):
        """Test that accepting invalid code raises ValueError."""
        generator = ShortCodeGenerator()
        
        with pytest.raises(ValueError, match="Invalid custom code"):
            generator.accept_custom_code("")
        
        with pytest.raises(ValueError, match="Invalid custom code"):
            generator.accept_custom_code("abc-123")
    
    def test_accept_custom_code_duplicate(self):
        """Test that accepting duplicate code raises ValueError."""
        generator = ShortCodeGenerator()
        generator.accept_custom_code("abc123")
        
        with pytest.raises(ValueError, match="Invalid custom code"):
            generator.accept_custom_code("abc123")
    
    def test_encode_base62_zero(self):
        """Test base62 encoding of zero."""
        generator = ShortCodeGenerator()
        assert generator.encode_base62(0) == "0"
    
    def test_encode_base62_positive(self):
        """Test base62 encoding of positive numbers."""
        generator = ShortCodeGenerator()
        assert generator.encode_base62(1) == "1"
        assert generator.encode_base62(10) == "A"
        assert generator.encode_base62(61) == "z"
        assert generator.encode_base62(62) == "10"
        assert generator.encode_base62(62*62) == "100"
    
    def test_encode_base62_negative(self):
        """Test that encoding negative number raises ValueError."""
        generator = ShortCodeGenerator()
        with pytest.raises(ValueError, match="Cannot encode negative numbers"):
            generator.encode_base62(-1)
    
    def test_decode_base62(self):
        """Test base62 decoding."""
        generator = ShortCodeGenerator()
        assert generator.decode_base62("0") == 0
        assert generator.decode_base62("1") == 1
        assert generator.decode_base62("A") == 10
        assert generator.decode_base62("z") == 61
        assert generator.decode_base62("10") == 62
        assert generator.decode_base62("100") == 62*62
    
    def test_decode_base62_invalid(self):
        """Test that decoding invalid string raises ValueError."""
        generator = ShortCodeGenerator()
        
        with pytest.raises(ValueError, match="Cannot decode empty string"):
            generator.decode_base62("")
        
        with pytest.raises(ValueError, match="Invalid base62 character"):
            generator.decode_base62("abc-123")
    
    def test_encode_decode_roundtrip(self):
        """Test that encode and decode are inverse operations."""
        generator = ShortCodeGenerator()
        test_numbers = [0, 1, 10, 100, 1000, 10000, 999999, 62*62*62-1]
        
        for number in test_numbers:
            encoded = generator.encode_base62(number)
            decoded = generator.decode_base62(encoded)
            assert decoded == number
    
    def test_generate_from_number(self):
        """Test generating code from number."""
        generator = ShortCodeGenerator()
        code = generator.generate_from_number(12345)
        assert code == generator.encode_base62(12345)
        assert code in generator.existing_codes
    
    def test_alphabet_completeness(self):
        """Test that BASE62_ALPHABET contains exactly 62 characters."""
        generator = ShortCodeGenerator()
        assert len(generator.BASE62_ALPHABET) == 62
        assert generator.BASE62_ALPHABET == (
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )


class TestConvenienceFunctions:
    """Test cases for convenience module-level functions."""
    
    def test_generate_random_code_function(self):
        """Test the generate_random_code convenience function."""
        code = generate_random_code(code_length=6)
        assert len(code) == 6
        assert code.isalnum()
    
    def test_generate_random_code_with_existing(self):
        """Test generate_random_code with existing codes."""
        existing = {"abc123"}
        code = generate_random_code(code_length=6, existing_codes=existing)
        assert code != "abc123"
    
    def test_validate_custom_code_function(self):
        """Test the validate_custom_code convenience function."""
        assert validate_custom_code("abc123") is True
        assert validate_custom_code("") is False
        assert validate_custom_code("abc-123") is False
    
    def test_validate_custom_code_with_existing(self):
        """Test validate_custom_code with existing codes."""
        existing = {"abc123"}
        assert validate_custom_code("abc123", existing_codes=existing) is False
        assert validate_custom_code("xyz789", existing_codes=existing) is True
    
    def test_encode_base62_function(self):
        """Test the encode_base62 convenience function."""
        assert encode_base62(0) == "0"
        assert encode_base62(62) == "10"
        assert encode_base62(1000).isalnum()
    
    def test_decode_base62_function(self):
        """Test the decode_base62 convenience function."""
        assert decode_base62("0") == 0
        assert decode_base62("10") == 62
        assert decode_base62(encode_base62(1000)) == 1000
    
    def test_encode_decode_functions_roundtrip(self):
        """Test that convenience functions work together."""
        test_numbers = [0, 1, 10, 100, 1000, 123456789]
        for number in test_numbers:
            encoded = encode_base62(number)
            decoded = decode_base62(encoded)
            assert decoded == number