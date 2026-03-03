"""Short code generator module for URL shortening.

This module provides functionality for generating short codes using
various methods including random generation, custom codes, and base62 encoding.
"""

import random
import string
from typing import Optional, Set


class CodeGenerator:
    """Generates short codes for URL shortening."""

    # Base62 character set (0-9, A-Z, a-z)
    BASE62_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def __init__(self, code_length: int = 6):
        """Initialize the code generator.

        Args:
            code_length: Default length for randomly generated codes.
        """
        self.code_length = code_length
        self._generated_codes: Set[str] = set()

    def generate_random(self, length: Optional[int] = None) -> str:
        """Generate a random short code.

        Args:
            length: Length of the code to generate. If not provided,
                   uses the default code_length from initialization.

        Returns:
            A randomly generated short code using uppercase, lowercase,
            and numeric characters.

        Raises:
            ValueError: If the requested length is less than 1.
        """
        if length is None:
            length = self.code_length
        if length < 1:
            raise ValueError("Code length must be at least 1")

        chars = string.ascii_letters + string.digits
        code = "".join(random.choice(chars) for _ in range(length))

        # Ensure uniqueness by regenerating if collision occurs
        if code in self._generated_codes:
            return self.generate_random(length)

        self._generated_codes.add(code)
        return code

    def validate_custom_code(self, code: str) -> bool:
        """Validate a custom short code.

        Args:
            code: The custom code to validate.

        Returns:
            True if the code is valid, False otherwise.

        A valid code must:
        - Be at least 1 character long
        - Contain only alphanumeric characters
        - Not exceed 100 characters
        """
        if not code or len(code) > 100:
            return False

        return code.isalnum()

    def set_custom_code(self, code: str) -> str:
        """Set a custom short code.

        Args:
            code: The custom code to set.

        Returns:
            The validated custom code.

        Raises:
            ValueError: If the code is invalid or already exists.
        """
        if not self.validate_custom_code(code):
            raise ValueError(
                "Custom code must be 1-100 alphanumeric characters"
            )

        if code in self._generated_codes:
            raise ValueError(f"Code '{code}' already exists")

        self._generated_codes.add(code)
        return code

    def encode_base62(self, number: int) -> str:
        """Encode a number to base62 string.

        Args:
            number: The number to encode. Must be non-negative.

        Returns:
            A base62 encoded string.

        Raises:
            ValueError: If the number is negative.
        """
        if number < 0:
            raise ValueError("Number must be non-negative")

        if number == 0:
            return self.BASE62_CHARS[0]

        encoded = []
        base = len(self.BASE62_CHARS)

        while number > 0:
            number, remainder = divmod(number, base)
            encoded.append(self.BASE62_CHARS[remainder])

        return "".join(reversed(encoded))

    def decode_base62(self, code: str) -> int:
        """Decode a base62 string to a number.

        Args:
            code: The base62 encoded string to decode.

        Returns:
            The decoded number.

        Raises:
            ValueError: If the code contains invalid characters.
        """
        result = 0
        base = len(self.BASE62_CHARS)

        for char in code:
            if char not in self.BASE62_CHARS:
                raise ValueError(
                    f"Invalid character '{char}' in base62 code"
                )
            result = result * base + self.BASE62_CHARS.index(char)

        return result

    def generate_from_number(self, number: int) -> str:
        """Generate a short code from a number using base62 encoding.

        Args:
            number: The number to encode.

        Returns:
            A base62 encoded short code.
        """
        code = self.encode_base62(number)

        # Ensure uniqueness
        if code in self._generated_codes:
            # Add a random suffix if collision occurs
            suffix = self.generate_random(2)
            code = f"{code}{suffix}"

        self._generated_codes.add(code)
        return code

    def is_unique(self, code: str) -> bool:
        """Check if a code is unique (not already generated).

        Args:
            code: The code to check.

        Returns:
            True if the code is unique, False otherwise.
        """
        return code not in self._generated_codes

    def clear_history(self) -> None:
        """Clear the history of generated codes.

        This is useful for testing or resetting the generator state.
        """
        self._generated_codes.clear()