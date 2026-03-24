"""
accent_identifier.py

Module responsible for analyzing parsed Sanskrit text representations
and mapping appropriate Vedic accent contours.

Vedic accent system (three-way):
  - Udatta (high): pitch_delta +1.0, code 2
  - Svarita (falling): pitch_delta +0.5, code 1
  - Anudatta (low): pitch_delta -1.0, code 0
"""

from typing import List, Dict, Optional
from backend.melodic import config


# SLP1 explicit accent markers
ACCENT_MARKERS = {
    '\u0301': 'udatta',      # Combining acute accent
    '^': 'udatta',           # Caret notation
    "'": 'udatta',           # Apostrophe
    '\u0300': 'svarita',     # Combining grave accent
    '_': 'svarita',          # Underscore notation
    '`': 'svarita',          # Backtick
}

ACCENT_CODE_MAP = {
    'udatta': 2,
    'svarita': 1,
    'anudatta': 0,
}


def extract_explicit_accent(syllable_text: str) -> Optional[str]:
    """
    Check for explicit accent marker in syllable string.
    
    Returns accent name if found, None otherwise.
    """
    for marker, accent_name in ACCENT_MARKERS.items():
        if marker in syllable_text:
            return accent_name
    return None


def clean_syllable_text(syllable_text: str) -> str:
    """Remove explicit accent markers from syllable string."""
    cleaned = syllable_text
    for marker in ACCENT_MARKERS.keys():
        cleaned = cleaned.replace(marker, '')
    return cleaned


def apply_rule_patterns(
    slp1: str,
    current_syllable: Dict,
    all_syllables: List[Dict],
    syllable_index: int
) -> str:
    """
    Apply contextual rule patterns from vedic_accent_rules.json.
    
    Rule priority:
    1. Position-based rules (first, last, penultimate)
    2. Weight-based patterns (guru/laghu)
    3. Metrical patterns (Anushtubh meter positions)
    4. Default to anudatta
    """
    try:
        rules = config.ACCENT_RULES
    except Exception:
        return 'anudatta'
    
    if not rules:
        return 'anudatta'
    
    total_syllables = len(all_syllables)
    weight = current_syllable.get('weight', 'L')
    
    # Position-based rules
    if 'position_rules' in rules:
        pos_rules = rules['position_rules']
        
        if syllable_index == 0 and 'first' in pos_rules:
            first_rule = pos_rules['first']
            if isinstance(first_rule, dict) and 'default_accent' in first_rule:
                return first_rule['default_accent']
            elif isinstance(first_rule, str):
                return first_rule
        
        if syllable_index == total_syllables - 1 and 'last' in pos_rules:
            last_rule = pos_rules['last']
            if isinstance(last_rule, dict) and 'default_accent' in last_rule:
                return last_rule['default_accent']
            elif isinstance(last_rule, str):
                return last_rule
        
        if syllable_index == total_syllables - 2 and 'penultimate' in pos_rules:
            penu_rule = pos_rules['penultimate']
            if isinstance(penu_rule, dict) and 'default_accent' in penu_rule:
                return penu_rule['default_accent']
            elif isinstance(penu_rule, str):
                return penu_rule
    
    # Weight-based patterns
    if 'weight_patterns' in rules:
        patterns = rules['weight_patterns']
        
        if weight == 'G' and 'guru' in patterns:
            guru_rule = patterns['guru']
            if isinstance(guru_rule, dict) and 'default_accent' in guru_rule:
                return guru_rule['default_accent']
            elif isinstance(guru_rule, str):
                return guru_rule
        
        if weight == 'L' and 'laghu' in patterns:
            laghu_rule = patterns['laghu']
            if isinstance(laghu_rule, dict) and 'default_accent' in laghu_rule:
                return laghu_rule['default_accent']
            elif isinstance(laghu_rule, str):
                return laghu_rule
    
    # Metrical stress patterns (Anushtubh meter)
    if 'meter_patterns' in rules and 'anushtubh' in rules['meter_patterns']:
        meter = rules['meter_patterns']['anushtubh']
        if 'stress_positions' in meter:
            stress_pos = meter['stress_positions']
            if isinstance(stress_pos, dict) and syllable_index in stress_pos:
                return stress_pos[syllable_index]
    
    return 'anudatta'


def identify_accents(slp1: str, syllables: List[Dict]) -> List[Dict]:
    """
    Identify Vedic accents for each syllable in input sequence.
    
    Args:
        slp1 (str): Canonical SLP1 transliterated text
        syllables (List[Dict]): Ordered syllable list with schema:
                                {"syllable": str, "weight": "L"|"G", "index": int}
    
    Returns:
        List[Dict]: Accent results aligned 1:1 with input syllables:
                    {"syllable": str, "accent_name": str, "accent_code": int}
                    
    Accent detection priority:
    1. Explicit markers in SLP1 syllable strings
    2. Rule patterns from vedic_accent_rules.json via config
    3. Default anudatta (code 0)
    
    Accent codes:
    - udatta: 2 (high pitch)
    - svarita: 1 (falling pitch)
    - anudatta: 0 (low pitch)
    """
    if not syllables:
        return []
    
    results = []
    
    for index, syllable_dict in enumerate(syllables):
        syllable_text = syllable_dict.get('syllable', '')
        
        # Priority 1: Check for explicit accent marker in syllable string
        explicit_accent = extract_explicit_accent(syllable_text)
        
        if explicit_accent:
            accent_name = explicit_accent
        else:
            # Priority 2: Apply contextual rule patterns
            accent_name = apply_rule_patterns(
                slp1,
                syllable_dict,
                syllables,
                index
            )
        
        # Map accent name to numeric code
        accent_code = ACCENT_CODE_MAP.get(accent_name, 0)
        
        # Build result entry with cleaned syllable text
        results.append({
            'syllable': clean_syllable_text(syllable_text),
            'accent_name': accent_name,
            'accent_code': accent_code,
        })
    
    return results


def test_identify_accents():
    """
    Test accent identification with manually annotated Rigvedic samples.
    """
    print("=" * 75)
    print("VEDIC ACCENT IDENTIFICATION TEST")
    print("=" * 75)
    
    # Sample 1: Rigveda 1.1.1 opening (agnim ile)
    # Annotated: I marked with ^ (udatta)
    sample1_slp1 = "agnim Ile"
    sample1_syllables = [
        {'syllable': 'a', 'weight': 'L', 'index': 0},
        {'syllable': 'gnim', 'weight': 'G', 'index': 1},
        {'syllable': 'I^', 'weight': 'G', 'index': 2},
        {'syllable': 'le', 'weight': 'L', 'index': 3},
    ]
    
    result1 = identify_accents(sample1_slp1, sample1_syllables)
    print("\nSample 1: agnim Ile")
    print("Expected: I syllable marked as udatta (code 2)")
    print("-" * 75)
    for res in result1:
        print(f"  {res['syllable']:8} → {res['accent_name']:10} (code: {res['accent_code']})")
    
    # Sample 2: With svarita marker
    sample2_slp1 = "yajna_vAham"
    sample2_syllables = [
        {'syllable': 'yaj', 'weight': 'G', 'index': 0},
        {'syllable': 'na_', 'weight': 'L', 'index': 1},
        {'syllable': 'vA', 'weight': 'G', 'index': 2},
        {'syllable': 'ham', 'weight': 'G', 'index': 3},
    ]
    
    result2 = identify_accents(sample2_slp1, sample2_syllables)
    print("\nSample 2: yajna_vAham")
    print("Expected: na marked with svarita (code 1)")
    print("-" * 75)
    for res in result2:
        print(f"  {res['syllable']:8} → {res['accent_name']:10} (code: {res['accent_code']})")
    
    # Sample 3: No explicit markers (rule-based only)
    sample3_slp1 = "indra"
    sample3_syllables = [
        {'syllable': 'in', 'weight': 'G', 'index': 0},
        {'syllable': 'dra', 'weight': 'L', 'index': 1},
    ]
    
    result3 = identify_accents(sample3_slp1, sample3_syllables)
    print("\nSample 3: indra (no explicit markers)")
    print("Expected: Rule-based accent assignment")
    print("-" * 75)
    for res in result3:
        print(f"  {res['syllable']:8} → {res['accent_name']:10} (code: {res['accent_code']})")
    
    print("\n" + "=" * 75)


if __name__ == '__main__':
    test_identify_accents()
