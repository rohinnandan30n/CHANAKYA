"""
Sanskrit NLP Text Preprocessor Module

This module provides text preprocessing functionality for Sanskrit language processing.
It handles input detection, transliteration scheme conversion, and text normalization.

Key Features:
- Detects input scheme (Devanagari, IAST, Harvard-Kyoto)
- Converts all input to SLP1 canonical form
- Cleans punctuation and extra whitespace
- Provides robust error handling and validation
- Logs unrecognized characters with warnings
- Handles edge cases: mixed scripts, missing diacritics, Latin characters

Dependencies:
- indic_transliteration: For conversion between Sanskrit transliteration schemes
- chanda: For Sanskrit metrical analysis
- sanskrit_text: For Sanskrit text utilities
"""

import re
import json
import logging
import os
from typing import Optional, Dict, Set, Tuple
from indic_transliteration import sanscript

# Configure logging for unrecognized characters
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s [%(name)s]: %(message)s'
)
logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    Handles Sanskrit text preprocessing and normalization.
    
    This class manages input detection, transliteration conversion, and text cleaning
    for Sanskrit language processing.
    """
    
    # Supported transliteration schemes
    SUPPORTED_SCHEMES = {
        'devanagari': sanscript.DEVANAGARI,
        'iast': sanscript.IAST,
        'harvard_kyoto': sanscript.HK,
        'hk': sanscript.HK,
        'slp1': sanscript.SLP1,
        'itrans': sanscript.ITRANS,
        'velthuis': sanscript.VELTHUIS,
        'wx': sanscript.WX,
    }
    
    # Devanagari Unicode range for detection
    DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]+')
    
    # IAST pattern: Latin letters with diacritics
    IAST_PATTERN = re.compile(
        r'[a-zA-Z\u0101\u0103\u0105\u0113\u0115\u0129\u012B\u014D\u0151\u0169\u016B\u0169]'
    )
    
    # Harvard-Kyoto pattern: ASCII letters, numbers, and special chars
    HARVARD_KYOTO_PATTERN = re.compile(r'[a-zA-Z0-9_]+')
    
    # Punctuation pattern for cleaning
    PUNCTUATION_PATTERN = re.compile(r'[^\w\s\u0900-\u097F]', re.UNICODE)
    
    @staticmethod
    def detect_scheme(text: str) -> str:
        """
        Detect the transliteration scheme of input text.
        
        This method analyzes the input text and determines whether it's in
        Devanagari, IAST, Harvard-Kyoto, or another recognized scheme.
        
        Args:
            text (str): The input text to analyze
            
        Returns:
            str: The detected scheme name ('devanagari', 'iast', 'harvard_kyoto', or 'unknown')
            
        Raises:
            ValueError: If the input text is empty
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        text = text.strip()
        
        # Check for Devanagari
        if TextPreprocessor.DEVANAGARI_PATTERN.search(text):
            return 'devanagari'
        
        # Check for IAST (has diacritical marks)
        if any(char in text for char in 'āēīōūṁṅñṭḍḻḹ'):
            return 'iast'
        
        # Check for SLP1 (has uppercase vowels/consonants like A, I, U, B, G, N, R, S, T)
        slp1_markers = set('AIUEOfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvzSsh')
        upper_chars = set(c for c in text if c.isupper())
        if upper_chars and upper_chars.issubset(slp1_markers):
            return 'slp1'
        
        # Check for Harvard-Kyoto (basic ASCII letters)
        if TextPreprocessor.HARVARD_KYOTO_PATTERN.match(text):
            return 'harvard_kyoto'
        
        return 'unknown'
    
    @staticmethod
    def load_rules() -> Dict:
        """
        Load Sanskrit transliteration rules from JSON configuration.
        
        Attempts to load rules from backend/data/linguistic/sanskrit_rules.json
        for scheme metadata and character mappings.
        
        Returns:
            Dict: Rules dictionary if file exists, empty dict otherwise
        """
        try:
            # Multiple possible paths depending on execution context
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '../../data/linguistic/sanskrit_rules.json'),
                os.path.join(os.getcwd(), 'backend/data/linguistic/sanskrit_rules.json'),
                'backend/data/linguistic/sanskrit_rules.json',
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        rules = json.load(f)
                    logger.debug(f"Loaded Sanskrit rules from {path}")
                    return rules
            
            logger.warning("Sanskrit rules file not found, using defaults")
            return {}
        except Exception as e:
            logger.warning(f"Failed to load Sanskrit rules: {e}")
            return {}
    
    @staticmethod
    def detect_unrecognized_characters(text: str, scheme: str) -> Set[str]:
        """
        Identify characters in text that may not be recognized in the given scheme.
        
        This helps us log problematic characters and provide user feedback about
        potential issues in the input text.
        
        Args:
            text (str): The input text to analyze
            scheme (str): The transliteration scheme ('devanagari', 'iast', 'hk')
            
        Returns:
            Set[str]: Set of unrecognized/unusual characters found
        """
        unrecognized = set()
        
        # Expected character ranges and patterns for each scheme
        expected_patterns = {
            'devanagari': {
                'ranges': [(0x0900, 0x097F)],  # Devanagari Unicode range
                'description': 'Devanagari script'
            },
            'iast': {
                'pattern': r'[a-zA-Z\u0101\u0103\u0105\u0113\u0115\u0129\u012B\u014D\u0151\u0169\u016B\u0169\s\d]',
                'description': 'Latin with diacritics'
            },
            'hk': {
                'pattern': r'[a-zA-Z\d\s]',
                'description': 'ASCII Latin characters'
            }
        }
        
        scheme_lower = scheme.lower()
        if scheme_lower not in expected_patterns:
            return unrecognized
        
        config = expected_patterns[scheme_lower]
        
        if 'ranges' in config:
            # Check for Devanagari
            valid_chars = set()
            for start, end in config['ranges']:
                valid_chars.update(chr(i) for i in range(start, end + 1))
            valid_chars.update(' \t\n\r')  # Allow whitespace
            
            for char in text:
                if char not in valid_chars and char not in '0123456789':
                    unrecognized.add(char)
        else:
            # Check against regex pattern
            pattern = config['pattern']
            for char in text:
                if not re.match(pattern, char):
                    unrecognized.add(char)
        
        return unrecognized
    
    @staticmethod
    def transliterate(text: str, from_scheme: str) -> Tuple[str, Dict]:
        """
        Convert Sanskrit text from one transliteration scheme to SLP1 (canonical form).
        
        This is a robust transliteration function that:
        1. Validates input and source scheme
        2. Detects unrecognized characters and logs warnings
        3. Converts text to SLP1 using indic_transliteration
        4. Handles edge cases like mixed scripts, missing diacritics
        5. Returns both the result and metadata about the conversion
        
        Supported input schemes:
        - 'devanagari': Devanagari script (देवनागरी)
        - 'iast': International Alphabet of Sanskrit Transliteration (Latin with marks)
        - 'hk': Harvard-Kyoto (ASCII-only)
        
        Args:
            text (str): The input text to transliterate
            from_scheme (str): Source scheme ('devanagari', 'iast', 'hk')
            
        Returns:
            Tuple[str, Dict]: (converted_text, metadata_dict) where metadata includes:
                - 'scheme': input scheme used
                - 'unrecognized_chars': set of chars that could not be placed
                - 'conversion_status': 'success', 'partial', or 'failed'
                - 'warnings': list of warning messages
                
        Raises:
            ValueError: If text is empty or scheme is unsupported
            TypeError: If input is not a string
            
        Examples:
            >>> # Devanagari input
            >>> result, meta = transliterate('नमस्ते', 'devanagari')
            >>> print(result)  # Output: 'namaste'
            >>> 
            >>> # IAST input
            >>> result, meta = transliterate('namaskar', 'iast')
            >>> 
            >>> # Handle unrecognized characters
            >>> result, meta = transliterate('नमस्ते Hello', 'devanagari')
            >>> if meta['unrecognized_chars']:
            ...     print(f"Warning: {meta['unrecognized_chars']}")
        """
        # Input validation
        if not isinstance(text, str):
            raise TypeError(f"Input text must be a string, got {type(text).__name__}")
        
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        # Normalize scheme name
        from_scheme = from_scheme.lower().strip()
        
        # Map scheme names to sanscript constants
        scheme_map = {
            'devanagari': sanscript.DEVANAGARI,
            'iast': sanscript.IAST,
            'hk': sanscript.HK,
            'harvard_kyoto': sanscript.HK,
            'slp1': sanscript.SLP1,
        }
        
        if from_scheme not in scheme_map:
            raise ValueError(
                f"Unsupported scheme '{from_scheme}'. "
                f"Supported schemes: {', '.join(scheme_map.keys())}"
            )
        
        # SLP1 is already canonical — return as-is
        if from_scheme == 'slp1':
            return text, {'scheme': 'slp1', 'unrecognized_chars': set(), 'conversion_status': 'success', 'warnings': [], 'character_count': len(text)}
        
        text = text.strip()
        metadata = {
            'scheme': from_scheme,
            'unrecognized_chars': set(),
            'conversion_status': 'success',
            'warnings': [],
            'character_count': len(text),
        }
        
        try:
            # Step 1: Detect unrecognized characters
            unrecognized = TextPreprocessor.detect_unrecognized_characters(text, from_scheme)
            if unrecognized:
                metadata['unrecognized_chars'] = unrecognized
                warning_msg = (
                    f"Found {len(unrecognized)} unrecognized character(s) for {from_scheme}: "
                    f"{repr(''.join(sorted(unrecognized)))}"
                )
                metadata['warnings'].append(warning_msg)
                logger.warning(warning_msg)
            
            # Step 2: Perform the transliteration using indic_transliteration
            # The library handles most edge cases gracefully, converting what it can
            source_scheme = scheme_map[from_scheme]
            slp1_text = sanscript.transliterate(
                text,
                source_scheme,
                sanscript.SLP1
            )
            
            # Step 3: Validate conversion result
            if not slp1_text:
                metadata['conversion_status'] = 'failed'
                raise ValueError("Transliteration resulted in empty string")
            
            # Step 4: Log conversion summary
            logger.debug(
                f"Transliterated {from_scheme.upper()} ({len(text)} chars) → "
                f"SLP1 ({len(slp1_text)} chars)"
            )
            
            # Step 5: Return both converted text and metadata
            return slp1_text, metadata
            
        except sanscript.SchemeNotSupportedError as e:
            metadata['conversion_status'] = 'failed'
            error_msg = f"Unsupported scheme in transliteration: {e}"
            metadata['warnings'].append(error_msg)
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        except Exception as e:
            metadata['conversion_status'] = 'partial'
            error_msg = f"Error during transliteration from {from_scheme}: {str(e)}"
            metadata['warnings'].append(error_msg)
            logger.error(error_msg)
            # Re-raise to let caller handle
            raise ValueError(error_msg)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text by removing punctuation and extra whitespace.
        
        This method:
        1. Removes extra whitespace
        2. Normalizes whitespace characters
        3. Removes punctuation (except for Devanagari script)
        4. Strips leading/trailing whitespace
        
        Args:
            text (str): The text to clean
            
        Returns:
            str: The cleaned text
        """
        if not text:
            return ""
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation but preserve Devanagari script
        text = TextPreprocessor.PUNCTUATION_PATTERN.sub('', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def accept_input(text: str, scheme: Optional[str] = None) -> str:
        """
        Process input text and convert it to SLP1 canonical form.
        
        This is the main entry point for text preprocessing. It:
        1. Detects or validates the input scheme
        2. Converts the text to SLP1 canonical form using transliterate()
        3. Cleans punctuation and whitespace
        4. Returns the normalized text
        
        Args:
            text (str): The input text to process
            scheme (str, optional): The input scheme ('devanagari', 'iast', 'harvard_kyoto', etc.)
                                   If not provided, it will be auto-detected.
        
        Returns:
            str: The text converted to SLP1 canonical form and cleaned
            
        Raises:
            ValueError: If text is empty, scheme is invalid, or conversion fails
            TypeError: If input is not a string
        
        Examples:
            >>> preprocessor = TextPreprocessor()
            >>> # Devanagari input
            >>> result = preprocessor.accept_input('नमस्ते')
            >>> # IAST input with explicit scheme
            >>> result = preprocessor.accept_input('namaste', scheme='iast')
            >>> # Auto-detected
            >>> result = preprocessor.accept_input('namaskar')
        """
        # Type validation
        if not isinstance(text, str):
            raise TypeError(f"Input text must be a string, got {type(text).__name__}")
        
        # Empty text validation
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        text = text.strip()
        
        # Detect scheme if not provided
        if scheme is None:
            detected_scheme = TextPreprocessor.detect_scheme(text)
            if detected_scheme == 'unknown':
                scheme = 'iast'  # Default to IAST for unknown schemes
            else:
                scheme = detected_scheme
        else:
            # Validate provided scheme
            scheme = scheme.lower()
            if scheme not in TextPreprocessor.SUPPORTED_SCHEMES:
                raise ValueError(
                    f"Unsupported scheme '{scheme}'. "
                    f"Supported schemes: {', '.join(TextPreprocessor.SUPPORTED_SCHEMES.keys())}"
                )
        
        try:
            # Use the robust transliterate function
            slp1_text, metadata = TextPreprocessor.transliterate(text, scheme)
            
            # Log any warnings from transliteration
            if metadata['warnings']:
                for warning in metadata['warnings']:
                    logger.warning(warning)
            
            # Clean the text (remove punctuation, extra whitespace)
            cleaned_text = TextPreprocessor.clean_text(slp1_text)
            
            if not cleaned_text:
                raise ValueError("Text became empty after processing")
            
            return cleaned_text
            
        except Exception as e:
            raise ValueError(
                f"Failed to convert text from '{scheme}' to SLP1: {str(e)}"
            )



# Module-level functions for convenience
def transliterate(text: str, from_scheme: str) -> Tuple[str, Dict]:
    """
    Convenience function to transliterate Sanskrit text to SLP1.
    
    This function creates a TextPreprocessor instance and transliterates the input text.
    It's a shorthand for TextPreprocessor.transliterate().
    
    Args:
        text (str): The input text to transliterate
        from_scheme (str): Source scheme ('devanagari', 'iast', 'hk')
    
    Returns:
        Tuple[str, Dict]: (converted_text, metadata_dict) where metadata includes:
            - 'scheme': input scheme used
            - 'unrecognized_chars': set of unrecognized chars
            - 'conversion_status': 'success', 'partial', or 'failed'
            - 'warnings': list of warning messages
    
    Raises:
        ValueError: If text is empty or conversion fails
        TypeError: If input is not a string
    """
    return TextPreprocessor.transliterate(text, from_scheme)


def accept_input(text: str, scheme: Optional[str] = None) -> str:
    """
    Convenience function to process Sanskrit text.
    
    This function creates a TextPreprocessor instance and processes the input text.
    It's a shorthand for TextPreprocessor.accept_input().
    
    Args:
        text (str): The input text to process
        scheme (str, optional): The input scheme. If not provided, it will be auto-detected.
    
    Returns:
        str: The text converted to SLP1 canonical form and cleaned
    
    Raises:
        ValueError: If text is empty or conversion fails
        TypeError: If input is not a string
    """
    return TextPreprocessor.accept_input(text, scheme)