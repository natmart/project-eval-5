"""Short code generator module for PyShort."""

import random
import string
from typing import List


class ShortCodeGenerator:
    """Generator for creating short codes for URLs."""
    
    # Default character set (no ambiguous characters like 0, O, 1, l, I)
    DEFAULT_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
    
    def __init__(self, chars: str | None = None, default_length: int = 6):
        """
        Initialize the short code generator.
        
        Args:
            chars: Character set to use for generating codes (defaults to DEFAULT_CHARS)
            default_length: Default length for generated codes
        """
        self.chars = chars or self.DEFAULT_CHARS
        self.default_length = default_length
        self.existing_codes: set = set()
    
    def generate(self, length: int | None = None) -> str:
        """
        Generate a new short code.
        
        Args:
            length: Length of the short code to generate ( defaults to default_length)
            
        Returns:
            A randomly generated short code
        """
        length = length or self.default_length
        
        # Generate a unique short code
        while True:
            code = ''.join(random.choice(self.chars) for _ in range(length))
            
            # Ensure we don't generate duplicates
            if code not in self.existing_codes:
                self.existing_codes.add(code)
                return code
    
    def register_code(self, code: str) -> None:
        """
        Register a short code as being used to avoid collisions.
        
        Args:
            code: The short code to register
        """
        self.existing_codes.add(code)
    
    def unregister_code(self, code: str) -> None:
        """
        Remove a short code from the registry.
        
        Args:
            code: The short code to unregister
        """
        self.existing_codes.discard(code)
    
    def has_code(self, code: str) -> bool:
        """
        Check if a code has been registered.
        
        Args:
            code: The short code to check
            
        Returns:
            True if the code is registered, False otherwise
        """
        return code in self.existing_codes
    
    def load_existing_codes(self, codes: List[str]) -> None:
        """
        Load existing short codes to avoid collisions.
        
        Args:
            codes: List of existing short codes
        """
        self.existing_codes.update(codes)
    
    def reset(self) -> None:
        """Reset the generator, clearing all registered codes."""
        self.existing_codes.clear()