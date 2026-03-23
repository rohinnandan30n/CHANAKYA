"""
Linguistic Analysis Runner

Task 5: Step 25 - Main runner that accepts verse strings and produces
structured JSON output with full linguistic analysis.

This module provides the primary entry point for complete Sanskrit linguistic
analysis, combining all Tasks 1-5.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Optional

from backend.linguistic import (
    accept_input,
    syllabify_and_mark,
    identify_chanda,
    LinguisticOutput,
    SyllableOutput,
    ChandaOutput,
    serialize_linguistic_data,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_verse(verse: str, input_scheme: str = 'auto') -> str:
    """
    Step 25: Complete linguistic analysis of a Sanskrit verse.
    
    Performs all tasks (1-5):
    - Task 1-2: Transliteration to SLP1
    - Task 3: Syllabification with Laghu-Guru marking
    - Task 4: Metrical scheme identification
    - Task 5: Structured JSON output
    
    Args:
        verse (str): Sanskrit text in any supported scheme
        input_scheme (str): 'auto' (detect), 'devanagari', 'iast', 'harvard_kyoto'
        
    Returns:
        str: JSON string with complete analysis
        
    Raises:
        ValueError: If analysis fails
        
    Examples:
        >>> json_result = analyze_verse("नमस्ते")
        >>> data = json.loads(json_result)
        >>> print(data['canonical_slp1'])
        'namasate'
        >>> print(data['chanda']['name'])
        'Anushtubh'
    """
    logger.info(f"Starting analysis of verse: {verse[:50]}...")
    
    try:
        # Step 1-2: Transliterate to SLP1
        logger.debug("Step 1-2: Transliteration")
        # Convert 'auto' to None for auto-detection
        scheme_param = None if input_scheme == 'auto' else input_scheme
        slp1_text = accept_input(verse, scheme_param)
        detected_scheme = 'unknown'  # TODO: track this from accept_input
        logger.debug(f"Transliterated to SLP1: {slp1_text}")
        
        # Step 3: Syllabification
        logger.debug("Step 3: Syllabification")
        syllables_marked = syllabify_and_mark(slp1_text)
        
        # Create SyllableOutput objects
        syllable_outputs = [
            SyllableOutput(syllable=syll, weight=weight, index=idx)
            for idx, (syll, weight) in enumerate(syllables_marked)
        ]
        
        # Get metrical pattern
        metrical_pattern = ''.join(weight for _, weight in syllables_marked)
        logger.debug(f"Metrical pattern: {metrical_pattern}")
        
        # Step 4: Identify metre
        logger.debug("Step 4: Metre Identification")
        chanda_result = identify_chanda(metrical_pattern)
        
        chanda_output = ChandaOutput(
            name=chanda_result['name'],
            syllables_per_pada=chanda_result['syllables_per_pada'],
            gana_pattern=chanda_result['gana_pattern'],
            classification=chanda_result.get('classification', 'unknown'),
            confidence=chanda_result['confidence'],
            notes=chanda_result.get('notes', ''),
            matra_count=chanda_result.get('matra_count'),
            example=chanda_result.get('example', '')
        )
        
        # Step 5: Create structured output
        logger.debug("Step 5: Structured Output Creation")
        output = LinguisticOutput(
            original_text=verse,
            input_scheme=detected_scheme,
            canonical_slp1=slp1_text,
            syllables=syllable_outputs,
            metrical_pattern=metrical_pattern,
            chanda=chanda_output
        )
        
        # Serialize to JSON
        json_output = serialize_linguistic_data(output)
        logger.info("Analysis completed successfully")
        
        return json_output
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise ValueError(f"Failed to analyze verse: {e}")


def main():
    """
    CLI Entry Point: python -m backend.linguistic.runner '<verse>'
    
    Accepts a Sanskrit verse as command-line argument and outputs
    complete analysis as pretty-printed JSON.
    
    Examples:
        $ python -m backend.linguistic.runner "नमस्ते"
        $ python -m backend.linguistic.runner "agnI medhA jushA RM"
    """
    if len(sys.argv) < 2:
        print("Usage: python -m backend.linguistic.runner '<verse>'")
        print("")
        print("Examples:")
        print("  python -m backend.linguistic.runner 'नमस्ते'")
        print("  python -m backend.linguistic.runner 'agnI medhA jushA RM'")
        print("")
        print("Supported Input Schemes:")
        print("  - Devanagari (नागरी)")
        print("  - IAST (Latin with diacritics)")
        print("  - Harvard-Kyoto (ASCII only)")
        print("  - SLP1 (Sanskrit Library Phonetic)")
        sys.exit(1)
    
    verse = sys.argv[1]
    
    try:
        json_output = analyze_verse(verse)
        print(json_output)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
