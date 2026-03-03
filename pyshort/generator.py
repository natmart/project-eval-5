"""Short code generator module for PyShort URL shortener.

This module provides functions to generate short codes with different strategies:
- Random alphanumeric codes (6 characters by default)
- Custom user-defined codes
- Base62 encoding for integer-based codes

The module ensures uniqueness and handles collisions through validation callbacks.
"""

import random
import string
from typing import Callable, Optional, Set


class ShortCodeGenerator:
    """Generator for short codes with multiple encoding strategies."""
    
    # Base62 alphabet: 0-9, A-Z, a-z (62 characters)
    BASE62_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
    
    def __init__(
        self,
        code_length: int = 6,
        existing_codes: Optional[Set[str]] = None,
        is_unique_callback: Optional[Callable[[str], bool]] = None,
    ):
        """Initialize the short code generator.
        
        Args:
            code_length: Length for randomly generated codes (default: 6).
            existing_codes: Set of already used codes for uniqueness checking.
            is_unique_callback: Callback function that returns True if a code is unique.
                This can be used to check against a database. If provided, it takes
                precedence over the existing_codes set.
        """
        if code_length < 1:
            raise ValueError("code_length must be at least 1")
        self.code_length = code_length
        self.existing_codes = existing_codes or set()
        self.is_unique_callback = is_unique_callback
    
    def _is_unique(self, code: str) -> bool:
        """Check if a code is unique.
        
        Args:
            code: The code to check.
            
        Returns:
            True if the code is unique, False otherwise.
        """
        if self.is_unique_callback:
            return self.is_unique_callback(code)
        return code not in self.existing_codes
    
    def _add_to_existing(self, code: str) -> None:
        """Add a code to the set of existing codes.
        
        This is only used when is_unique_callback is not provided.
        
        Args:
            code: The code to add.
        """
        if not self.is_unique_callback:
            self.existing_codes.add(code)
    
    def generate_random_code(self, max_attempts: int = 100) -> str:
        """Generate a random alphanumeric short code.
        
        The code will consist of uppercase letters, lowercase letters, and digits.
        This method continuously generates codes until a unique one is found.
        
        Args:
            max_attempts: Maximum number of attempts to generate a unique code.
                If reached, RuntimeError is raised.
                
        Returns:
            A unique random short code.
            
        Raises:
            RuntimeError: If unable to generate a unique code within max_attempts.
        """
        for _ in range(max_attempts):
            code = "".join(
                random.choices(string.ascii_letters + string.digits, k=self.code_length)
            )
            if self._is_unique(code):
                self._add_to_existing(code)
                return code
        
        raise RuntimeError(
            f"Failed to generate unique code after {max_attempts} attempts. "
            "Consider increasing code_length or reviewing existing codes."
        )
    
    def validate_custom_code(self, code: str) -> bool:
        """Validate a custom user-defined code.
        
        Args:
            code: The custom code to validate.
            
        Returns:
            True if the code is valid and unique, False otherwise.
        """
        if not code:
            return False
        # Only allow alphanumeric characters
        if not code.isalnum():
            return False
        return self._is_unique(code)
    
    def accept_custom_code(self, code: str) -> str:
        """Accept and register a custom user-defined code.
        
        Args:
            code: The custom code to accept.
            
        Returns:
            The accepted code.
            
        Raises:
            ValueError: If the code is invalid or not unique.
        """
        if not self.validate_custom_code(code):
            raise ValueError(
                f"Invalid custom code '{code}'. "
                "Code must be alphanumeric and unique."
            )
        self._add_to_existing(code)
        return code
    
    def encode_base62(self, number: int) -> str:
        """Encode a number to base62 string.
        
        Args:
            number: The non-negative integer to encode.
            
        Returns:
            The base62 encoded string.
            
        Raises:
            ValueError: If number is negative.
        """
        if number < 0:
            raise ValueError("Cannot encode negative numbers")
        
        if number == 0:
            return self.BASE62_ALPHABET[0]
        
        encoded = []
        base = len(self.BASE62_ALPHABET)
        
        while number > 0:
            number, remainder = divmod(number, base)
            encoded.append(self.BASE62_ALPHABET[remainder])
        
        return "".join(reversed(encoded))
    
    def decode_base62(self, encoded: str) -> int:
        """Decode a base62 string to a number.
        
        Args:
            encoded: The base32 encoded string to decode.
            
        Returns:
            The decoded integer.
            
        Raises:
            ValueError: If encoded contains invalid characters.
        """
        if not encoded:
            raise ValueError("Cannot decode empty string")
        
        number = 0
        base = len(self.BASE62_ALPHABET)
        
        for char in encoded:
            if char not in self.BASE62_ALPHABET:
                raise ValueError(f"Invalid base62 character: '{char}'")
            number = number * base + self.BASE62_ALPHABET.index(char)
        
        return number
    
    def generate_from_number(self, number: int) -> str:
        """Generate a short code from a number using base62 encoding.
        
        This is useful when you have sequential IDs and want to encode them
        into shorter codes.
        
        Args:
            number: The non-negative integer to encode.
            
        Returns:
            The base62 encoded short code.
            
        Raises:
            ValueError: If number is negative.
        """
        code = self.encode_base62(number)
        self._add_to_existing(code)
        return code


# Convenience functions for simple use cases

def generate_random_code(
    code_length: int = 6,
    existing_codes: Optional[Set[str]] = None,
    is_unique_callback: Optional[Callable[[str], bool]] = None,
    max_attempts: int = 100,
) -> str:
    """Generate a random alphanumeric short code.
    
    This is a convenience function that creates a ShortCodeGenerator
    and generates a single random code.
    
    Args:
        code_length: Length for the random code (default: 6).
        existing_codes: Set of already used codes.
        is_unique_callback: Callback to check code uniqueness.
        max_attempts: Maximum generation attempts.
        
    Returns:
        A unique random short code.
    """
    generator = ShortCodeGenerator(
        code_length=code_length,
        existing_codes=existing_codes,
        is_unique_callback=is_unique_callback,
    )
    return generator.generate_random_code(max_attempts=max_attempts)


def validate_custom_code(
    code: str,
    existing_codes: Optional[Set[str]] = None,
    is_unique_callback: Optional[Callable[[str], bool]] = None,
) -> bool:
    """Validate a custom user-defined code.
    
    This is a convenience function that creates a ShortCodeGenerator
    and validates a custom code.
    
    Args:
        code: The custom code to validate.
        existing_codes: Set of already used codes.
        is_unique_callback: Callback to check code uniqueness.
        
    Returns:
        True if the code is valid and unique, False otherwise.
    """
    generator = ShortCodeGenerator(
        existing_codes=existing_codes,
        is_unique_callback=is_unique_callback,
    )
    return generator.validate_custom_code(code)


def encode_base62(number: int) -> str:
    """Encode a number to base62 string.
    
    This is a convenience function for base62 encoding.
    
    Args:
        number: The non-negative integer to encode.
        
    Returns:
        The base62 encoded string.
    """
    generator = ShortCodeGenerator()
    return generator.encode_base62(number)


def decode_base62(encoded: str) -> int:
    """Decode a base62 string to a number.
    
    This is a convenience function for base62 decoding.
    
    Args:
        encoded: The base62 encoded string to decode.
        
    Returns:
        The decoded integer.
    """
    generator = ShortCodeGenerator()
    return generator.decode_base62(encoded)