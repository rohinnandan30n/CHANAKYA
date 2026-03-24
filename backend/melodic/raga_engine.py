"""
raga_engine.py

Core processing engine for conforming structural melodic contours into
the specific grammar, rules, and notes of a parameterized Raga.

Converts F0 contours to raga-constrained sequences and generates MIDI.
"""

import math
from typing import List, Dict

from backend.melodic import config

# Note name to semitone offset relative to Sa (equal temperament model)
NOTE_SEMITONES = {
    "S": 0,     # Sa (unison)
    "R": 2,     # Re (Shuddh) - major second
    "r": 1,     # Re (Komal) - minor second
    "G": 4,     # Ga (Shuddh) - major third
    "g": 3,     # Ga (Komal) - minor third
    "M": 5,     # Ma (Shuddh) - perfect fourth
    "M~": 6,    # Ma (Tivra) - augmented fourth
    "P": 7,     # Pa (perfect fifth)
    "D": 9,     # Dha (Shuddh) - major sixth
    "d": 8,     # Dha (Komal) - minor sixth
    "N": 11,    # Ni (Shuddh) - major seventh
    "n": 10,    # Ni (Komal) - minor seventh
}

BASE_SA_HZ = 140.0
A4_HZ = 440.0
MIDI_A4 = 69


def select_raga(chanda_name: str) -> dict:
    """
    Select a raga based on the linguistic chanda (metrical) classification.
    
    Mapping:
        Anushtubh → Bhairav
        Trishtubh → Yaman
        Unknown → Yaman (default)
    
    Args:
        chanda_name (str): Name of the identified chanda/metre.
        
    Returns:
        dict: Full raga definition from config.RAGA_DEFS
        
    Raises:
        KeyError: If selected raga not found
    """
    chanda_to_raga = {
        "Anushtubh": "Bhairav",
        "Trishtubh": "Yaman",
    }
    
    raga_name = chanda_to_raga.get(chanda_name, "Yaman")
    
    try:
        return config.get_raga(raga_name)
    except (KeyError, AttributeError):
        # Fallback to Yaman
        if "Yaman" in config.RAGA_DEFS:
            return config.RAGA_DEFS["Yaman"]
        raise ValueError(f"No raga found for chanda: {chanda_name}")


def note_to_frequency(note_name: str, base_sa_hz: float = BASE_SA_HZ) -> float:
    """
    Convert a raga note name to frequency in Hz.
    
    Uses equal temperament relative to Sa.
    
    Args:
        note_name (str): Note name (S, R, G, M, P, D, N, etc.)
        base_sa_hz (float): Frequency of Sa in Hz
        
    Returns:
        float: Frequency in Hz
    """
    # Normalize note name
    note = note_name.strip() if isinstance(note_name, str) else "S"
    
    semitones = NOTE_SEMITONES.get(note, 0)
    ratio = 2.0 ** (semitones / 12.0)
    return base_sa_hz * ratio


def build_scale_frequencies(raga: dict, base_sa_hz: float = BASE_SA_HZ) -> Dict[str, float]:
    """
    Build a dictionary of allowed frequencies for a raga.
    
    Uses the "notes" field from raga definition if available,
    otherwise collects unique notes from arohana and avarohana.
    
    Args:
        raga (dict): Raga definition dictionary
        base_sa_hz (float): Base Sa frequency
        
    Returns:
        Dict[str, float]: Mapping of note names to frequencies
    """
    scale_freqs = {}
    
    # Prefer explicit "notes" list
    if "notes" in raga and isinstance(raga["notes"], list):
        all_notes = raga["notes"]
    else:
        # Fall back to collecting from arohana/avarohana
        all_notes = set()
        if "arohana" in raga and isinstance(raga["arohana"], list):
            all_notes.update(raga["arohana"])
        if "avarohana" in raga and isinstance(raga["avarohana"], list):
            all_notes.update(raga["avarohana"])
    
    for note in all_notes:
        freq = note_to_frequency(note, base_sa_hz)
        scale_freqs[note] = freq
    
    return scale_freqs


def find_nearest_raga_frequency(
    target_f0: float,
    scale_freqs: Dict[str, float]
) -> float:
    """
    Find the nearest allowed raga frequency to a target F0.
    
    Args:
        target_f0 (float): Target frequency in Hz
        scale_freqs (Dict[str, float]): Available raga note frequencies
        
    Returns:
        float: Nearest allowed frequency
    """
    if not scale_freqs:
        return target_f0
    
    nearest_freq = min(
        scale_freqs.values(),
        key=lambda f: abs(f - target_f0)
    )
    
    return nearest_freq


def constrain_to_raga(
    pitch_sequence: List[Dict],
    raga: Dict
) -> List[Dict]:
    """
    Snap pitch contour to raga scale, preserving durations and order.
    
    Args:
        pitch_sequence (List[Dict]): Input with "syllable", "f0_hz", "duration_ms"
        raga (Dict): Raga definition with notes, arohana, avarohana
        
    Returns:
        List[Dict]: Constrained sequence aligned 1:1:
                    {"syllable": str, "f0_hz": float, "duration_ms": float}
    """
    if not pitch_sequence:
        return []
    
    # Build available frequencies from raga
    scale_freqs = build_scale_frequencies(raga)
    
    if not scale_freqs:
        return pitch_sequence
    
    results = []
    
    for item in pitch_sequence:
        f0_hz = item["f0_hz"]
        
        # Find nearest allowed frequency
        snapped_f0 = find_nearest_raga_frequency(f0_hz, scale_freqs)
        
        results.append({
            "syllable": item["syllable"],
            "f0_hz": snapped_f0,
            "duration_ms": item["duration_ms"],
        })
    
    return results


def generate_midi(pitch_sequence: List[Dict]) -> List[int]:
    """
    Convert F0 frequencies to MIDI note numbers.
    
    Uses standard formula: midi = 69 + 12 * log2(f0 / 440)
    
    Args:
        pitch_sequence (List[Dict]): Input with "f0_hz" field
        
    Returns:
        List[int]: MIDI note numbers aligned 1:1 with input
    """
    midi_notes = []
    
    for item in pitch_sequence:
        f0_hz = item.get("f0_hz", 440.0)
        
        if f0_hz <= 0:
            midi_note = 0
        else:
            midi_note = MIDI_A4 + 12 * math.log2(f0_hz / A4_HZ)
            midi_note = round(midi_note)
        
        midi_notes.append(midi_note)
    
    return midi_notes


def test_raga_engine():
    """
    Test raga engine with sample pitch contour.
    """
    print("=" * 80)
    print("RAGA ENGINE TEST")
    print("=" * 80)
    
    # Sample pitch contour
    pitch_sequence = [
        {"syllable": "a", "f0_hz": 140.0, "duration_ms": 833.33},
        {"syllable": "gnim", "f0_hz": 160.0, "duration_ms": 1666.67},
        {"syllable": "i", "f0_hz": 180.0, "duration_ms": 833.33},
    ]
    
    print("\nInput Pitch Sequence:")
    for item in pitch_sequence:
        print(f"  {item['syllable']:8} F0={item['f0_hz']:6.1f} Hz, "
              f"Duration={item['duration_ms']:7.2f} ms")
    
    # Test 1: Raga selection
    print("\n--- Test 1: Raga Selection ---")
    raga_anushtubh = select_raga("Anushtubh")
    print(f"Anushtubh → Raga selected")
    
    raga_unknown = select_raga("Unknown")
    print(f"Unknown → Raga selected (default)")
    
    # Test 2: Constrain to raga
    print("\n--- Test 2: Constrain to Raga ---")
    constrained = constrain_to_raga(pitch_sequence, raga_anushtubh)
    print("Snapped F0 values:")
    for i, item in enumerate(constrained):
        orig_f0 = pitch_sequence[i]["f0_hz"]
        new_f0 = item["f0_hz"]
        print(f"  {item['syllable']:8} {orig_f0:6.1f} → {new_f0:6.1f} Hz")
    
    # Verify length preservation
    assert len(constrained) == len(pitch_sequence), "Length mismatch"
    print(f"✓ Length preserved: {len(constrained)} syllables")
    
    # Verify snapped frequencies are in raga scale
    scale_freqs = build_scale_frequencies(raga_anushtubh)
    freq_values = set(scale_freqs.values())
    all_in_scale = all(
        any(abs(item["f0_hz"] - freq) < 0.1 for freq in freq_values)
        for item in constrained
    )
    if all_in_scale:
        print("✓ All snapped frequencies in raga scale")
    else:
        print("✗ Some frequencies out of raga scale")
    
    # Test 3: Generate MIDI
    print("\n--- Test 3: Generate MIDI ---")
    midi_notes = generate_midi(constrained)
    print(f"MIDI notes: {midi_notes}")
    assert len(midi_notes) == len(pitch_sequence), "MIDI length mismatch"
    print(f"✓ MIDI length preserved: {len(midi_notes)} notes")
    
    print("\n" + "=" * 80)
    print("✅ Raga engine tests PASSED")
    print("=" * 80)


if __name__ == "__main__":
    test_raga_engine()
