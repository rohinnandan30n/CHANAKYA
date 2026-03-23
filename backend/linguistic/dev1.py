"""
Dev1: Linguistic Processing Pipeline

Orchestrates: text_preprocessor → syllabifier → chanda_identifier → output_serializer
"""

try:
    from .text_preprocessor import TextPreprocessor
    from .syllabifier import Syllabifier
    from .chanda_identifier import ChandaIdentifier
    from .output_serializer import (
        LinguisticOutput, SyllableOutput, ChandaOutput, 
        MetadataOutput, serialize_linguistic_data
    )
except ImportError:
    from text_preprocessor import TextPreprocessor
    from syllabifier import Syllabifier
    from chanda_identifier import ChandaIdentifier
    from output_serializer import (
        LinguisticOutput, SyllableOutput, ChandaOutput, 
        MetadataOutput, serialize_linguistic_data
    )

import json
from typing import Dict, Any


def process_text(text: str) -> Dict[str, Any]:
    """
    Process Sanskrit text through linguistic pipeline.
    
    Pipeline Steps:
    1. Text Preprocessing: Detect scheme, transliterate to SLP1, clean
    2. Syllabification: Break into syllables, mark Laghu/Guru weights
    3. Chanda Identification: Identify metrical scheme from weight pattern
    4. Output Serialization: Create structured Pydantic models
    
    Args:
        text (str): Input Sanskrit text (any supported scheme)
        
    Returns:
        Dict: Structured analysis with syllables, weights, chanda info
    """
    
    try:
        # STEP 1: Clean text and convert to SLP1
        canonical_slp1 = TextPreprocessor.accept_input(text)
        input_scheme = TextPreprocessor.detect_scheme(text)
        
        # STEP 2: Syllabify and mark weights
        syllabifier = Syllabifier()
        syllables_marked = syllabifier.syllabify_and_mark(canonical_slp1)
        
        # Extract syllables and weights
        syllable_list = [syl for syl, weight in syllables_marked]
        weight_list = [weight for syl, weight in syllables_marked]
        
        # STEP 3: Identify chanda (metrical scheme)
        chanda_info = ChandaIdentifier.identify_chanda(weight_list)
        
        # STEP 4: Create Pydantic models
        # Create SyllableOutput objects
        syllable_outputs = [
            SyllableOutput(
                syllable=syl,
                weight=weight,
                index=i
            )
            for i, (syl, weight) in enumerate(zip(syllable_list, weight_list))
        ]
        
        # Create ChandaOutput object
        chanda_output = ChandaOutput(
            name=chanda_info.get('name', 'unknown'),
            syllables_per_pada=chanda_info.get('syllables_per_pada', len(syllable_list)),
            gana_pattern=chanda_info.get('gana_pattern', ''.join(weight_list)),
            classification=chanda_info.get('classification', 'unknown'),
            confidence=chanda_info.get('confidence', 0.0)
        )
        
        # Create LinguisticOutput object
        output = LinguisticOutput(
            original_text=text,
            input_scheme=input_scheme,
            canonical_slp1=canonical_slp1,
            syllables=syllable_outputs,
            chanda=chanda_output
        )
        
        # STEP 5: Serialize to JSON-compatible dict
        return output.model_dump()
        
    except Exception as e:
        # Error handling with stage info
        return {
            "error": str(e),
            "stage": "linguistic_processing",
            "status": "failed"
        }


def serialize_output(text: str) -> str:
    """
    Process text and return JSON string representation.
    
    Args:
        text (str): Input Sanskrit text
        
    Returns:
        str: JSON string of analysis
    """
    result_dict = process_text(text)
    return json.dumps(result_dict, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Test with sample Sanskrit text
    test_text = "राH"
    result = process_text(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))