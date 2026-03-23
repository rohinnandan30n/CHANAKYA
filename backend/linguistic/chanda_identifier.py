"""
Chanda (Metrical Scheme) Identifier Module

This module identifies classical Sanskrit metrical schemes (chandas)
from syllable weight patterns (Laghu-Guru sequences).

Common Chandas:
- Anushtubh: 8 syllables per pada (GGGG LGGG pattern)
- Tristubh: 11 syllables per pada
- Jagati: 12 syllables per pada
- Pankti: 5 syllables per pada
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ChandaIdentifier:
    """
    Identifies Sanskrit metrical schemes from syllable weight patterns.
    """
    
    # Common chanda patterns (simplified)
    CHANDA_PATTERNS = {
        'Anushtubh': {
            'syllables_per_pada': 8,
            'typical_pattern': 'GGGG LGGG',
            'classification': 'sama',
            'frequency': 'most_common'
        },
        'Tristubh': {
            'syllables_per_pada': 11,
            'typical_pattern': 'LGGG LLGG LGGG',
            'classification': 'sama',
            'frequency': 'common'
        },
        'Jagati': {
            'syllables_per_pada': 12,
            'typical_pattern': 'LGGG LGGG LGGG',
            'classification': 'sama',
            'frequency': 'common'
        },
        'Pankti': {
            'syllables_per_pada': 5,
            'typical_pattern': 'GLLGL',
            'classification': 'ardhasama',
            'frequency': 'rare'
        }
    }
    
    @staticmethod
    def identify_chanda(weights: List[str]) -> Dict[str, any]:
        """
        Identify the metrical scheme from a sequence of weights.
        
        Args:
            weights (List[str]): List of 'L' (Laghu) and 'G' (Guru) weights
            
        Returns:
            Dict: Chanda information with name, confidence, pattern, etc.
        """
        if not weights:
            return {
                'name': 'unknown',
                'syllables_per_pada': 0,
                'gana_pattern': '',
                'classification': 'unknown',
                'confidence': 0.0,
            }
        
        pattern = ''.join(weights)
        syllable_count = len(weights)
        
        # Try to match known chandas
        best_match = None
        best_confidence = 0.0
        
        for chanda_name, chanda_info in ChandaIdentifier.CHANDA_PATTERNS.items():
            expected_count = chanda_info['syllables_per_pada']
            
            # Check if syllable count matches
            if syllable_count == expected_count:
                expected_pattern = chanda_info['typical_pattern'].replace(' ', '')
                
                # Simple matching: count matching positions
                match_count = sum(1 for i, (a, b) in enumerate(zip(pattern, expected_pattern)) if a == b)
                confidence = match_count / len(expected_pattern)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = chanda_name
        
        # Return result
        if best_match:
            chanda_info = ChandaIdentifier.CHANDA_PATTERNS[best_match]
            return {
                'name': best_match,
                'syllables_per_pada': chanda_info['syllables_per_pada'],
                'gana_pattern': pattern,
                'classification': chanda_info['classification'],
                'confidence': best_confidence,
            }
        else:
            # Unknown chanda - return based on syllable count heuristic
            return {
                'name': 'Unknown',
                'syllables_per_pada': syllable_count,
                'gana_pattern': pattern,
                'classification': 'unknown',
                'confidence': 0.0,
            }
    
    @staticmethod
    def get_chanda_info(chanda_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific chanda.
        
        Args:
            chanda_name (str): Name of the chanda
            
        Returns:
            Dict or None: Chanda information or None if not found
        """
        return ChandaIdentifier.CHANDA_PATTERNS.get(chanda_name)


# Convenience function
def identify_chanda(weights: List[str]) -> Dict[str, any]:
    """
    Convenience function to identify chanda from weights.
    
    Args:
        weights (List[str]): List of 'L' and 'G' weights
        
    Returns:
        Dict: Chanda identification result
    """
    return ChandaIdentifier.identify_chanda(weights)
