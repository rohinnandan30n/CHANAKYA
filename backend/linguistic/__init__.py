"""
Linguistic processing module for Sanskrit NLP.

This module provides utilities for Sanskrit text processing, including
transliteration detection, conversion, text normalization, syllabification,
metrical scheme identification, and structured output serialization.
"""

from .text_preprocessor import TextPreprocessor, accept_input, transliterate
from .syllabifier import Syllabifier, syllabify_and_mark, get_syllables, get_metrical_pattern, identify_chanda
from .output_serializer import (
    LinguisticOutput, 
    SyllableOutput, 
    ChandaOutput, 
    MetadataOutput,
    serialize_linguistic_data,
    validate_output_schema
)

__all__ = [
    'TextPreprocessor',
    'accept_input',
    'transliterate',
    'Syllabifier',
    'syllabify_and_mark',
    'get_syllables',
    'get_metrical_pattern',
    'identify_chanda',
    'LinguisticOutput',
    'SyllableOutput',
    'ChandaOutput',
    'MetadataOutput',
    'serialize_linguistic_data',
    'validate_output_schema',
]
