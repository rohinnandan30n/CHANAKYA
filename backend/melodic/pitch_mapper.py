"""
pitch_mapper.py

Module for mapping Vedic accents to pitch (F0) and duration values.
Converts accent codes and syllable weights to musical parameters.
"""

from typing import List, Dict

ACCENT_TO_F0 = {
    2: 220.0,
    1: 180.0,
    0: 140.0,
}

LAGHU = "L"
GURU = "G"


def calculate_mora_duration(tempo_bpm: int) -> float:
    """
    Calculate duration of one mora in milliseconds based on tempo.
    
    Args:
        tempo_bpm (int): Tempo in beats per minute.
        
    Returns:
        float: Duration of one mora in milliseconds.
    """
    return 60000.0 / tempo_bpm


def get_syllable_duration(weight: str, mora_duration_ms: float) -> float:
    """
    Calculate duration for a syllable based on its weight.
    
    Args:
        weight (str): "L" for Laghu (1 mora) or "G" for Guru (2 mora).
        mora_duration_ms (float): Duration of one mora in milliseconds.
        
    Returns:
        float: Duration in milliseconds.
    """
    if weight == GURU:
        return 2.0 * mora_duration_ms
    else:
        return mora_duration_ms


def smooth_f0_contour(f0_values: List[float]) -> List[float]:
    """
    Apply smooth F0 transitions to avoid abrupt jumps.
    
    Uses light neighbor blending to maintain melodic contour while
    avoiding sharp jumps. Preserves base values more strongly.
    
    Args:
        f0_values (List[float]): Raw F0 values from accent mapping.
        
    Returns:
        List[float]: Smoothed F0 values.
    """
    if len(f0_values) <= 1:
        return f0_values
    
    smoothed = []
    
    for i, f0 in enumerate(f0_values):
        neighbor_avg = f0
        neighbor_count = 1
        
        if i > 0:
            neighbor_avg += f0_values[i - 1]
            neighbor_count += 1
        
        if i < len(f0_values) - 1:
            neighbor_avg += f0_values[i + 1]
            neighbor_count += 1
        
        neighbor_avg = neighbor_avg / neighbor_count
        
        # 80% current value, 20% neighbor average
        adjusted = (f0 * 0.8) + (neighbor_avg * 0.2)
        smoothed.append(adjusted)
    
    return smoothed


def map_pitch_duration(
    syllables: List[Dict],
    accents: List[Dict],
    tempo_bpm: int = 72
) -> List[Dict]:
    """
    Map Vedic accents and syllable weights to pitch (F0) and duration.
    
    Args:
        syllables (List[Dict]): Syllable data with "syllable", "weight", "index".
        accents (List[Dict]): Accent data with "syllable", "accent_name", "accent_code".
        tempo_bpm (int): Tempo in beats per minute. Default: 72 BPM.
        
    Returns:
        List[Dict]: Pitch-duration mapping aligned 1:1 with input:
                    {"syllable": str, "f0_hz": float, "duration_ms": float}
                    
    Raises:
        ValueError: If syllables and accents lists have different lengths.
    """
    if len(syllables) != len(accents):
        raise ValueError(
            f"Syllables and accents length mismatch: {len(syllables)} vs {len(accents)}"
        )
    
    mora_duration_ms = calculate_mora_duration(tempo_bpm)
    
    # Step 1: Extract raw F0 values from accents
    f0_values = []
    for accent in accents:
        accent_code = accent.get("accent_code", 0)
        f0 = ACCENT_TO_F0.get(accent_code, 140.0)
        f0_values.append(f0)
    
    # Step 2: Smooth F0 transitions
    smoothed_f0 = smooth_f0_contour(f0_values)
    
    # Step 3: Calculate durations
    durations = [
        get_syllable_duration(syllables[i]["weight"], mora_duration_ms)
        for i in range(len(syllables))
    ]
    
    # Step 4: Build output
    results = [
        {
            "syllable": syllables[i]["syllable"],
            "f0_hz": smoothed_f0[i],
            "duration_ms": durations[i],
        }
        for i in range(len(syllables))
    ]
    
    return results


def test_map_pitch_duration():
    """
    Test pitch and duration mapping with Rigvedic samples.
    """
    print("=" * 80)
    print("PITCH AND DURATION MAPPING TEST")
    print("=" * 80)
    
    # Sample 1: agnim (a-gnim)
    syllables_1 = [
        {"syllable": "a", "weight": "L", "index": 0},
        {"syllable": "gnim", "weight": "G", "index": 1},
    ]
    accents_1 = [
        {"syllable": "a", "accent_name": "anudatta", "accent_code": 0},
        {"syllable": "gnim", "accent_name": "udatta", "accent_code": 2},
    ]
    
    result_1 = map_pitch_duration(syllables_1, accents_1, tempo_bpm=72)
    print("\nSample 1: agnim")
    print("Tempo: 72 BPM, Mora duration: 833.33 ms")
    for item in result_1:
        print(f"  {item['syllable']:6} F0={item['f0_hz']:6.1f} Hz, "
              f"Duration={item['duration_ms']:7.2f} ms")
    
    f0_seq_1 = [item["f0_hz"] for item in result_1]
    max_jump_1 = max(abs(f0_seq_1[i] - f0_seq_1[i+1]) for i in range(len(f0_seq_1)-1))
    print(f"Max F0 jump: {max_jump_1:.1f} Hz (should be < 100 Hz)")
    assert max_jump_1 < 100.0, f"F0 jump too large: {max_jump_1}"
    
    # Sample 2: indra (i-ndra)
    syllables_2 = [
        {"syllable": "i", "weight": "L", "index": 0},
        {"syllable": "ndra", "weight": "L", "index": 1},
    ]
    accents_2 = [
        {"syllable": "i", "accent_name": "anudatta", "accent_code": 0},
        {"syllable": "ndra", "accent_name": "svarita", "accent_code": 1},
    ]
    
    result_2 = map_pitch_duration(syllables_2, accents_2, tempo_bpm=80)
    print("\nSample 2: indra")
    print("Tempo: 80 BPM, Mora duration: 750.00 ms")
    for item in result_2:
        print(f"  {item['syllable']:6} F0={item['f0_hz']:6.1f} Hz, "
              f"Duration={item['duration_ms']:7.2f} ms")
    
    f0_seq_2 = [item["f0_hz"] for item in result_2]
    max_jump_2 = max(abs(f0_seq_2[i] - f0_seq_2[i+1]) for i in range(len(f0_seq_2)-1))
    print(f"Max F0 jump: {max_jump_2:.1f} Hz (should be < 100 Hz)")
    assert max_jump_2 < 100.0, f"F0 jump too large: {max_jump_2}"
    
    # Sample 3: vāyu (vA-yu)
    syllables_3 = [
        {"syllable": "vA", "weight": "G", "index": 0},
        {"syllable": "yu", "weight": "L", "index": 1},
    ]
    accents_3 = [
        {"syllable": "vA", "accent_name": "udatta", "accent_code": 2},
        {"syllable": "yu", "accent_name": "anudatta", "accent_code": 0},
    ]
    
    result_3 = map_pitch_duration(syllables_3, accents_3, tempo_bpm=60)
    print("\nSample 3: vāyu")
    print("Tempo: 60 BPM, Mora duration: 1000.00 ms")
    for item in result_3:
        print(f"  {item['syllable']:6} F0={item['f0_hz']:6.1f} Hz, "
              f"Duration={item['duration_ms']:7.2f} ms")
    
    f0_seq_3 = [item["f0_hz"] for item in result_3]
    max_jump_3 = max(abs(f0_seq_3[i] - f0_seq_3[i+1]) for i in range(len(f0_seq_3)-1))
    print(f"Max F0 jump: {max_jump_3:.1f} Hz (should be < 100 Hz)")
    assert max_jump_3 < 100.0, f"F0 jump too large: {max_jump_3}"
    
    print("\n" + "=" * 80)
    print("All tests completed successfully.")


if __name__ == "__main__":
    test_map_pitch_duration()
