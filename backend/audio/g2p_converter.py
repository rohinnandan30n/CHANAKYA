"""
g2p_converter.py - Dev 3: Neural Audio Engineer
Grapheme-to-Phoneme converter for Sanskrit SLP1 input.
Uses mlphon for Indic G2P conversion.
"""

import logging
from typing import List
from sandhi_processor import load_sandhi_rules, apply_sandhi

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# SLP1 Sanskrit conjunct consonants mapping
CONJUNCTS = {
    "kS": "kʂ",   # kSa
    "jJ": "dʑ",   # jJa
    "tS": "tʃ",
    "dZ": "dʒ",
}

# SLP1 to IPA basic mapping for Sanskrit
SLP1_TO_IPA = {
    # Vowels - short
    "a": "ə", "i": "ɪ", "u": "ʊ", "f": "r̩", "x": "l̩",
    # Vowels - long
    "A": "aː", "I": "iː", "U": "uː", "F": "r̩ː", "X": "l̩ː",
    # Diphthongs
    "e": "eː", "E": "aɪ", "o": "oː", "O": "aʊ",
    # Gutturals
    "k": "k", "K": "kʰ", "g": "ɡ", "G": "ɡʰ", "N": "ŋ",
    # Palatals
    "c": "tɕ", "C": "tɕʰ", "j": "dʑ", "J": "dʑʰ", "Y": "ɲ",
    # Retroflexes
    "w": "ʈ", "W": "ʈʰ", "q": "ɖ", "Q": "ɖʰ", "R": "ɳ",
    # Dentals
    "t": "t̪", "T": "t̪ʰ", "d": "d̪", "D": "d̪ʰ", "n": "n",
    # Labials
    "p": "p", "P": "pʰ", "b": "b", "B": "bʰ", "m": "m",
    # Semivowels
    "y": "j", "r": "r", "l": "l", "v": "ʋ",
    # Sibilants
    "S": "ʃ", "z": "ʂ", "s": "s",
    # Aspirate
    "h": "ɦ",
    # Special
    "M": "ṃ",  # anusvara
    "H": "ḥ",  # visarga
}


class G2PConverter:
    """Sanskrit Grapheme-to-Phoneme converter using SLP1 encoding."""

    def __init__(self, model_path: str = "backend/data/models/g2p",
                 sandhi_rules_path: str = "sandhi_rules.json"):
        self.model_path = model_path
        self.sandhi_rules = self._load_sandhi_rules(sandhi_rules_path)
        self._mlphon_available = self._check_mlphon()
        logger.debug(f"G2PConverter initialized | mlphon: {self._mlphon_available}")

    def _load_sandhi_rules(self, path: str) -> list:
        try:
            return load_sandhi_rules(path)
        except FileNotFoundError:
            logger.warning("sandhi_rules.json not found, skipping sandhi preprocessing")
            return []

    def _check_mlphon(self) -> bool:
        try:
            import mlphon
            return True
        except ImportError:
            logger.warning("mlphon not available, falling back to rule-based G2P")
            return False

    def _apply_conjuncts(self, slp1_text: str) -> str:
        """Handle Sanskrit conjunct consonants before phoneme conversion."""
        result = slp1_text
        for conjunct, ipa in CONJUNCTS.items():
            result = result.replace(conjunct, ipa)
        return result

    def _rule_based_convert(self, slp1_text: str) -> List[str]:
        """Fallback rule-based SLP1 to IPA conversion."""
        phonemes = []
        i = 0
        text = slp1_text

        while i < len(text):
            # Try 2-char conjuncts first
            if i + 1 < len(text) and text[i:i+2] in CONJUNCTS:
                phonemes.append(CONJUNCTS[text[i:i+2]])
                i += 2
            elif text[i] in SLP1_TO_IPA:
                phonemes.append(SLP1_TO_IPA[text[i]])
                i += 1
            else:
                phonemes.append(text[i])
                i += 1

        return phonemes

    def convert(self, slp1_text: str) -> List[str]:
        """
        Convert SLP1 text to phonemes.

        Args:
            slp1_text: Sanskrit text in SLP1 encoding

        Returns:
            List of IPA/SAMPA phoneme strings

        Raises:
            ValueError: For empty or invalid input
        """
        if not slp1_text or not slp1_text.strip():
            raise ValueError("Input text cannot be empty")

        # Basic SLP1 validation
        valid_chars = set(SLP1_TO_IPA.keys()) | {" ", "-"}
        invalid = [c for c in slp1_text if c not in valid_chars]
        if invalid:
            logger.warning(f"Possibly non-SLP1 characters found: {invalid}")

        # Step 1: Apply sandhi rules
        tokens = slp1_text.strip().split()
        if self.sandhi_rules and len(tokens) > 1:
            slp1_text = apply_sandhi(tokens, self.sandhi_rules)
            logger.debug(f"After sandhi: {slp1_text}")

        # Step 2: Handle conjuncts
        processed = self._apply_conjuncts(slp1_text)

        # Step 3: Convert to phonemes
        if self._mlphon_available:
            try:
                import mlphon
                phonemes = mlphon.get_phonemes(slp1_text)
                logger.debug(f"mlphon phonemes: {phonemes}")
                return phonemes if isinstance(phonemes, list) else [phonemes]
            except Exception as e:
                logger.warning(f"mlphon failed: {e}, falling back to rule-based")

        # Fallback to rule-based
        phonemes = self._rule_based_convert(processed)
        logger.debug(f"Rule-based phonemes: {phonemes}")
        return phonemes


# Module-level converter instance
_converter = None

def convert(slp1_text: str) -> List[str]:
    """Module-level convert function."""
    global _converter
    if _converter is None:
        _converter = G2PConverter()
    return _converter.convert(slp1_text)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python g2p_converter.py '<slp1_word>'")
        print("Example: python g2p_converter.py 'namaH'")
        sys.exit(1)

    slp1_input = sys.argv[1]
    converter = G2PConverter()

    try:
        result = converter.convert(slp1_input)
        print(f"Input (SLP1): {slp1_input}")
        print(f"Phonemes:     {result}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
