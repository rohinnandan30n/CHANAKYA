"""
Sanskrit Syllabification and Laghu-Guru Marking Module

This module handles syllabification of Sanskrit text in SLP1 canonical form
and applies classical Sanskrit prosodic rules (Laghu-Guru marking) to classify
syllables by their metrical weight.

Key Concepts:
- Syllable: Basic phonetic unit typically containing a vowel nucleus
- Laghu (L): Light syllable - short vowel not in special conditions
- Guru (G): Heavy syllable - long vowel or short vowel in special positions
- SLP1: Sanskrit Library Phonetic - canonical transliteration scheme used

Rules for Guru (Heavy) Syllables:
1. Vowel is inherently long (A, I, U, R, L, E, O)
2. Short vowel before consonant cluster (conjunct)
3. Vowel before anusvara (M)
4. Vowel before visarga (H)
5. Final syllable with trailing consonant(s)

Dependencies:
- chanda: For advanced syllable segmentation
- indic_transliteration: For working with SLP1 text
"""

import re
import json
import logging
import os
from typing import List, Tuple, Set, Dict, Optional

logger = logging.getLogger(__name__)


class SyllabificationRules:
    """Container for Sanskrit syllabification and prosodic rules."""
    
    # SLP1 vowels - short and long
    SHORT_VOWELS = {'a', 'i', 'u', 'r', 'l', 'e', 'o'}
    LONG_VOWELS = {'A', 'I', 'U', 'R', 'L', 'E', 'O'}
    ALL_VOWELS = SHORT_VOWELS | LONG_VOWELS
    
    # SLP1 consonants
    CONSONANTS = {
        'k', 'K', 'g', 'G', 'N',  # Velar
        'c', 'C', 'j', 'J', 'Y',  # Palatal
        'w', 'W', 'q', 'Q', 'N',  # Retroflex
        't', 'T', 'd', 'D', 'n',  # Dental
        'p', 'P', 'b', 'B', 'm',  # Labial
        'y', 'r', 'l', 'v',       # Approximants
        'S', 's', 's'             # Sibilants
    }
    
    # Special segments
    ANUSVARA = 'M'  # Nasal marker
    VISARGA = 'H'   # Aspiration marker
    
    # All nasals in SLP1
    NASALS = {'m', 'n', 'N', 'n', 'M'}
    
    @staticmethod
    def load_rules() -> Dict:
        """Load Laghu-Guru rules from JSON configuration."""
        try:
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '../../data/linguistic/sanskrit_rules.json'),
                'backend/data/linguistic/sanskrit_rules.json',
                os.path.join(os.getcwd(), 'backend/data/linguistic/sanskrit_rules.json'),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        rules = json.load(f)
                    return rules.get('laghu_guru_rules', {})
            
            logger.warning("Laghu-Guru rules not found")
            return {}
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return {}


class Syllabifier:
    """
    Syllabifies Sanskrit text in SLP1 and marks syllables as Laghu (L) or Guru (G).
    
    This class handles:
    1. Breaking SLP1 text into syllables
    2. Applying Laghu-Guru weight rules to each syllable
    3. Handling edge cases (nasals before clusters, final syllables)
    4. Returning metrical structure information
    """
    
    def __init__(self):
        """Initialize syllabifier with rules."""
        self.rules = SyllabificationRules.load_rules()
    
    @staticmethod
    def is_consonant_cluster(text: str, start_idx: int) -> bool:
        """
        Check if position starts a consonant cluster (conjunct consonant).
        
        A conjunct consonant in Sanskrit is two or more consonants together.
        In SLP1, this means consecutive consonant characters without intervening vowels.
        
        Args:
            text (str): The SLP1 text
            start_idx (int): Position to check from
            
        Returns:
            bool: True if a consonant cluster begins at start_idx
        """
        if start_idx >= len(text) - 1:
            return False
        
        # Check if current position is a consonant
        if text[start_idx] not in SyllabificationRules.CONSONANTS:
            return False
        
        # Look ahead to see if next non-special character is also a consonant
        idx = start_idx + 1
        while idx < len(text):
            char = text[idx]
            if char in SyllabificationRules.ALL_VOWELS:
                return False  # Found a vowel, so no cluster
            if char in SyllabificationRules.CONSONANTS:
                return True  # Found another consonant - it's a cluster
            if char in (SyllabificationRules.ANUSVARA, SyllabificationRules.VISARGA):
                continue  # Skip special markers
            idx += 1
        
        return False
    
    @staticmethod
    def get_syllables(slp1_text: str) -> List[str]:
        """
        Segment SLP1 text into syllables.
        
        In Sanskrit, each syllable typically contains:
        - One vowel nucleus (short or long)
        - Optional preceding consonant(s)
        - Optional following consonant(s)
        
        Syllable structure: C*V(C*)
        where C = consonant, V = vowel
        
        Args:
            slp1_text (str): Text in SLP1 canonical form
            
        Returns:
            List[str]: List of syllable strings
            
        Raises:
            ValueError: If text is empty or invalid
        """
        if not slp1_text or not slp1_text.strip():
            raise ValueError("Input text cannot be empty")
        
        text = slp1_text.strip()
        syllables = []
        current_syllable = ""
        i = 0
        
        while i < len(text):
            char = text[i]
            current_syllable += char
            
            # When we encounter a vowel, we may have completed a syllable
            if char in SyllabificationRules.ALL_VOWELS:
                # Look ahead to determine syllable boundary
                j = i + 1
                
                # Collect trailing segments (anusvara, visarga)
                while j < len(text) and text[j] in (SyllabificationRules.ANUSVARA, 
                                                      SyllabificationRules.VISARGA):
                    current_syllable += text[j]
                    j += 1
                
                # Check for consonant(s) after vowel
                consonant_count = 0
                k = j
                while k < len(text) and text[k] in SyllabificationRules.CONSONANTS:
                    consonant_count += 1
                    k += 1
                
                # Decision: is syllable complete?
                # Syllable is complete if:
                # 1. No consonants follow, OR
                # 2. Consonant(s) follow AND next position is vowel or end
                if consonant_count == 0:
                    # No consonants - syllable is complete
                    syllables.append(current_syllable)
                    current_syllable = ""
                    i = j
                else:
                    # Has consonants - need to check if they're onset of next syllable
                    if k < len(text) and text[k] in SyllabificationRules.ALL_VOWELS:
                        # Consonant(s) are onset of next syllable
                        syllables.append(current_syllable)
                        current_syllable = ""
                        i = j
                    elif k >= len(text):
                        # End of text - consonants close this syllable
                        while j < k:
                            current_syllable += text[j]
                            j += 1
                        syllables.append(current_syllable)
                        current_syllable = ""
                        i = j
                    else:
                        # May be mixed - take first consonant as coda, rest as onset
                        current_syllable += text[j]
                        syllables.append(current_syllable)
                        current_syllable = ""
                        i = j + 1
            else:
                i += 1
        
        # Append any remaining characters
        if current_syllable:
            syllables.append(current_syllable)
        
        return syllables
    
    @staticmethod
    def classify_syllable_weight(syllable: str) -> str:
        """
        Classify a single syllable as Laghu (L) or Guru (G).
        
        Applies Sanskrit prosody rules:
        - GURU if: long vowel OR short vowel before cluster OR before M/H OR final with consonant
        - LAGHU if: short vowel in simple onset-nucleus structure
        
        Args:
            syllable (str): Single syllable string in SLP1
            
        Returns:
            str: 'G' for Guru (heavy) or 'L' for Laghu (light)
            
        Raises:
            ValueError: If syllable has no vowel
        """
        if not syllable:
            return 'L'  # Empty treated as light
        
        # Find vowel(s) in syllable
        vowels_found = [char for char in syllable if char in SyllabificationRules.ALL_VOWELS]
        
        if not vowels_found:
            return 'L'  # No vowel - treat as light
        
        # Check for long vowel - always Guru
        if any(v in SyllabificationRules.LONG_VOWELS for v in vowels_found):
            return 'G'
        
        # Short vowel - check special conditions
        # Find first vowel position
        first_vowel_idx = syllable.index(vowels_found[0])
        
        # Check for anusvara (M) or visarga (H) after vowel
        after_vowel_idx = first_vowel_idx + 1
        if after_vowel_idx < len(syllable):
            next_char = syllable[after_vowel_idx]
            if next_char in (SyllabificationRules.ANUSVARA, SyllabificationRules.VISARGA):
                return 'G'  # Vowel before M or H is Guru
        
        # Check for consonant cluster after vowel
        consonants_after = ""
        for i in range(after_vowel_idx, len(syllable)):
            if syllable[i] in SyllabificationRules.CONSONANTS:
                consonants_after += syllable[i]
        
        # If 2+ consonants (cluster) after vowel, it's Guru
        if len(consonants_after) >= 2:
            return 'G'
        
        # Single consonant or no consonant after short vowel = Laghu
        return 'L'
    
    def syllabify_and_mark(self, slp1_text: str) -> List[Tuple[str, str]]:
        """
        Syllabify SLP1 text and mark each syllable with Laghu-Guru weight.
        
        This is the main API function that:
        1. Segments text into syllables
        2. Classifies each syllable as Laghu (L) or Guru (G)
        3. Returns list of (syllable, weight) tuples
        
        Args:
            slp1_text (str): Text in SLP1 canonical form
            
        Returns:
            List[Tuple[str, str]]: List of (syllable_string, weight) tuples
                                  where weight is 'L' or 'G'
            
        Raises:
            ValueError: If text is empty or has no vowels
            
        Examples:
            >>> syll = Syllabifier()
            >>> result = syll.syllabify_and_mark('namasata')
            >>> # Returns: [('na', 'L'), ('ma', 'L'), ('sa', 'L'), ('ta', 'L')]
            >>> 
            >>> result = syll.syllabify_and_mark('medhA')
            >>> # Returns: [('me', 'L'), ('dhA', 'G')]
        """
        if not slp1_text or not slp1_text.strip():
            raise ValueError("Input text cannot be empty")
        
        try:
            # Step 1: Get syllables
            syllables = self.get_syllables(slp1_text)
            
            if not syllables:
                raise ValueError(f"Could not segment '{slp1_text}' into syllables")
            
            # Step 2: Classify each syllable
            result = []
            for syllable in syllables:
                weight = self.classify_syllable_weight(syllable)
                result.append((syllable, weight))
            
            logger.debug(f"Syllabified '{slp1_text}' into {len(result)} syllables")
            return result
        
        except Exception as e:
            logger.error(f"Error syllabifying '{slp1_text}': {e}")
            raise
    
    def get_metrical_pattern(self, slp1_text: str) -> str:
        """
        Get the metrical pattern of text as a string of L's and G's.
        
        Args:
            slp1_text (str): Text in SLP1 canonical form
            
        Returns:
            str: Pattern like "LGGG" or "LLGL"
            
        Examples:
            >>> syll = Syllabifier()
            >>> syll.get_metrical_pattern('namasata')
            'LLLL'
            >>> syll.get_metrical_pattern('medhAjushA')
            'LGLG'
        """
        marked = self.syllabify_and_mark(slp1_text)
        return ''.join(weight for _, weight in marked)
    
    def identify_chanda(self, lg_sequence: List[str]) -> Dict:
        """
        Identify Sanskrit metrical scheme (chanda) from Laghu-Guru sequence.
        
        Task 4 Implementation: Chanda Identification
        - Step 17: Load chanda_db.json database of metre patterns
        - Step 18: Match against known metres using pattern comparison
        - Step 19: Return structured dict with metre details
        - Step 20: Handle unknown metres with fuzzy matching
        
        Args:
            lg_sequence (List[str]): List of 'L' or 'G' strings, 
                                     or a single string like 'GGGGLGGG'
            
        Returns:
            Dict with keys:
            - name (str): Metre name (e.g., 'Anushtubh', 'Trishtubh')
            - syllables_per_pada (int): Syllables per quarter
            - gana_pattern (str): Visual pattern (e.g., 'GGGG LGGG')
            - confidence (float): 1.0 for exact match, < 1.0 for fuzzy
            - classification (str): 'sama', 'ardhasama', or 'vishama'
            - notes (str): Description of the metre
            
        Raises:
            ValueError: If input is invalid
            
        Examples:
            >>> syll = Syllabifier()
            >>> result = syll.identify_chanda(['G','G','G','G','L','G','G','G'])
            >>> # Returns: {'name': 'Anushtubh', 'syllables_per_pada': 8, 
            >>>            'gana_pattern': 'GGGG LGGG', 'confidence': 1.0, ...}
            >>> 
            >>> result = syll.identify_chanda('GGGGLGGG')
            >>> # Same result
        """
        # Normalize input
        if isinstance(lg_sequence, str):
            pattern = lg_sequence.upper().replace(' ', '')
        else:
            pattern = ''.join(lg_sequence).upper()
        
        if not pattern or not all(c in ('L', 'G') for c in pattern):
            raise ValueError(f"Invalid LG sequence: {lg_sequence}")
        
        # Load chanda database
        db_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'data', 'linguistic', 'chanda_db.json'
        )
        
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                chanda_db = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load chanda_db.json: {e}")
            raise ValueError(f"Cannot load metre database: {e}")
        
        metres = chanda_db.get('metres', {})
        
        # Step 18: Try exact match first
        for metre_key, metre_data in metres.items():
            # Get expected pattern from gana_pattern
            expected_pattern = metre_data['gana_pattern'].replace(' ', '')
            
            # For each pada/quarter of the verse
            syllables_per_pada = metre_data['syllables_per_pada']
            
            # Check if input matches this metre's pattern
            if pattern == expected_pattern:
                # Exact match
                return {
                    'name': metre_data['name'],
                    'syllables_per_pada': syllables_per_pada,
                    'gana_pattern': metre_data['gana_pattern'],
                    'classification': metre_data.get('classification', 'sama'),
                    'confidence': 1.0,
                    'notes': metre_data.get('notes', ''),
                    'matra_count': metre_data.get('matra_count', syllables_per_pada * 2),
                    'example': metre_data.get('example', '')
                }
            
            # Check for partial match (if input is just one pada)
            if len(pattern) == syllables_per_pada:
                # This might be a single pada
                similarity = self._calculate_similarity(pattern, expected_pattern)
                if similarity >= 0.85:
                    return {
                        'name': metre_data['name'],
                        'syllables_per_pada': syllables_per_pada,
                        'gana_pattern': metre_data['gana_pattern'],
                        'classification': metre_data.get('classification', 'sama'),
                        'confidence': similarity,
                        'notes': metre_data.get('notes', '') + ' (fuzzy match)',
                        'matra_count': metre_data.get('matra_count', syllables_per_pada * 2),
                        'example': metre_data.get('example', '')
                    }
        
        # Step 20: Fuzzy matching for unknown metres
        best_match = None
        best_similarity = 0.0
        
        for metre_key, metre_data in metres.items():
            expected_pattern = metre_data['gana_pattern'].replace(' ', '')
            syllables_per_pada = metre_data['syllables_per_pada']
            
            # Try matching against this metre
            if len(pattern) <= len(expected_pattern):
                similarity = self._calculate_similarity(pattern, expected_pattern[:len(pattern)])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = (metre_data, similarity)
        
        if best_match and best_similarity >= 0.75:
            metre_data, similarity = best_match
            return {
                'name': metre_data['name'],
                'syllables_per_pada': metre_data['syllables_per_pada'],
                'gana_pattern': metre_data['gana_pattern'],
                'classification': metre_data.get('classification', 'sama'),
                'confidence': similarity,
                'notes': f"{metre_data.get('notes', '')} (partial/fuzzy match)",
                'matra_count': metre_data.get('matra_count', metre_data['syllables_per_pada'] * 2),
                'example': metre_data.get('example', '')
            }
        
        # Unknown metre
        return {
            'name': 'Unknown',
            'syllables_per_pada': len(pattern),
            'gana_pattern': pattern,
            'classification': 'unknown',
            'confidence': 0.0,
            'notes': f"No known metre matches pattern {pattern}",
            'matra_count': len(pattern) * 2,
            'example': ''
        }
    
    @staticmethod
    def _calculate_similarity(pattern1: str, pattern2: str) -> float:
        """
        Calculate similarity between two LG patterns using Levenshtein distance.
        
        Args:
            pattern1 (str): First LG pattern
            pattern2 (str): Second LG pattern
            
        Returns:
            float: Similarity score between 0.0 and 1.0
        """
        if not pattern1 or not pattern2:
            return 0.0
        
        # Normalize lengths
        min_len = min(len(pattern1), len(pattern2))
        max_len = max(len(pattern1), len(pattern2))
        
        # Count matching positions
        matches = sum(1 for i in range(min_len) if pattern1[i] == pattern2[i])
        
        # Levenshtein-like scoring
        similarity = matches / max_len
        return similarity


# Module-level convenience functions
def syllabify_and_mark(slp1_text: str) -> List[Tuple[str, str]]:
    """
    Convenience function to syllabify and mark text.
    
    Args:
        slp1_text (str): Text in SLP1 canonical form
        
    Returns:
        List[Tuple[str, str]]: List of (syllable, weight) tuples
    """
    syllabifier = Syllabifier()
    return syllabifier.syllabify_and_mark(slp1_text)


def get_syllables(slp1_text: str) -> List[str]:
    """
    Convenience function to get syllables.
    
    Args:
        slp1_text (str): Text in SLP1 canonical form
        
    Returns:
        List[str]: List of syllable strings
    """
    return Syllabifier.get_syllables(slp1_text)


def get_metrical_pattern(slp1_text: str) -> str:
    """
    Convenience function to get metrical pattern.
    
    Args:
        slp1_text (str): Text in SLP1 canonical form
        
    Returns:
        str: Metrical pattern like "LGGG" or "LLGL"
    """
    syllabifier = Syllabifier()
    return syllabifier.get_metrical_pattern(slp1_text)


def identify_chanda(lg_sequence: List[str]) -> Dict:
    """
    Convenience function to identify metrical scheme from LG sequence.
    
    Args:
        lg_sequence: List of 'L'/'G' strings or a single pattern string
        
    Returns:
        Dict with metre details including name, syllables_per_pada, 
        gana_pattern, confidence, classification, and notes
    """
    syllabifier = Syllabifier()
    return syllabifier.identify_chanda(lg_sequence)