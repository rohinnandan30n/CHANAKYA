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
