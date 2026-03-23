"""
Linguistic processing module for Sanskrit NLP.

This module provides utilities for Sanskrit text processing, including
transliteration detection, conversion, text normalization, and syllabification.
"""

from .text_preprocessor import TextPreprocessor, accept_input, transliterate
from .syllabifier import Syllabifier, syllabify_and_mark, get_syllables, get_metrical_pattern

__all__ = [
    'TextPreprocessor',
    'accept_input',
    'transliterate',
    'Syllabifier',
    'syllabify_and_mark',
    'get_syllables',
    'get_metrical_pattern',
]
