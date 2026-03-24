import json
from typing import Dict, List

from backend.linguistic.runner import analyze_verse
from backend.melodic.accent_identifier import identify_accents
from backend.melodic.pitch_mapper import map_pitch_duration
from backend.melodic.raga_engine import select_raga, constrain_to_raga, generate_midi
from backend.melodic.explainer import explain_melodic_choice

def _validate_raga_snapping(
    pitch_original: List[Dict], 
    pitch_snapped: List[Dict]
) -> None:
    assert len(pitch_snapped) == len(pitch_original), (
        f"Raga snapping length mismatch: {len(pitch_snapped)} vs {len(pitch_original)}"
    )
    for i, (orig, snapped) in enumerate(zip(pitch_original, pitch_snapped)):
        assert "f0_hz" in snapped, f"snapped[{i}] missing 'f0_hz'"
        deviation = abs(snapped["f0_hz"] - orig["f0_hz"])
        assert deviation < 60, (
            f"snapped[{i}] deviation too large: {deviation:.1f} Hz (max: 60)"
        )


def _validate_midi_output(
    syllables: List[Dict], 
    midi_notes: List[int]
) -> None:
    assert isinstance(midi_notes, list), "MIDI output must be a list"
    assert len(midi_notes) == len(syllables), (
        f"MIDI length mismatch: {len(midi_notes)} vs {len(syllables)}"
    )
    for i, note in enumerate(midi_notes):
        assert isinstance(note, int), f"MIDI[{i}] not an integer"
        assert 40 <= note <= 80, (
            f"MIDI[{i}] out of range: {note} (expected 40-80)"
        )

RIGVEDIC_SAMPLES = [
    "agním īḷe purohitaṃ",
    "indraṃ mitraṃ varuṇam",
    "vāyum agnim",
]

def _assert_syllable_shape(syllables: List[Dict]) -> None:
    assert isinstance(syllables, list), "'syllables' must be a list"
    for i, item in enumerate(syllables):
        assert isinstance(item, dict), f"syllables[{i}] must be a dict"
        assert "syllable" in item
        assert "weight" in item
        assert "index" in item

def _validate_accent_output(syllables: List[Dict], accents: List[Dict]) -> None:
    assert len(accents) == len(syllables), (
        f"Accent output length mismatch: expected {len(syllables)}, got {len(accents)}"
    )
    for a in accents:
        assert "syllable" in a
        assert "accent_name" in a
        assert "accent_code" in a
        assert a["accent_code"] in (0, 1, 2)


def _validate_pitch_output(syllables: List[Dict], pitches: List[Dict]) -> None:
    assert len(pitches) == len(syllables), (
        f"Pitch output length mismatch: expected {len(syllables)}, got {len(pitches)}"
    )
    for i, p in enumerate(pitches):
        assert "syllable" in p, f"pitch[{i}] missing 'syllable'"
        assert "f0_hz" in p, f"pitch[{i}] missing 'f0_hz'"
        assert "duration_ms" in p, f"pitch[{i}] missing 'duration_ms'"
        assert isinstance(p["f0_hz"], (int, float)), f"pitch[{i}] f0_hz not numeric"
        assert isinstance(p["duration_ms"], (int, float)), f"pitch[{i}] duration_ms not numeric"
        assert 120 <= p["f0_hz"] <= 240, (
            f"pitch[{i}] F0 out of range: {p['f0_hz']} Hz (expected 120-240)"
        )
        assert p["duration_ms"] > 0, f"pitch[{i}] duration must be > 0"


def _check_f0_smoothness(pitches: List[Dict]) -> None:
    f0_values = [p["f0_hz"] for p in pitches]
    if len(f0_values) > 1:
        max_jump = max(abs(f0_values[i] - f0_values[i + 1]) for i in range(len(f0_values) - 1))
        assert max_jump < 100, (
            f"F0 jump too large: {max_jump:.1f} Hz (max allowed: 100 Hz)"
        )

def run_integration_harness() -> None:
    print("=" * 80)
    print("SVARA-CHANDA: FULL MELODIC PIPELINE INTEGRATION TEST")
    print("LINGUISTIC -> ACCENT -> PITCH -> RAGA -> MIDI -> EXPLANATION")
    print("=" * 80)

    for verse_idx, verse in enumerate(RIGVEDIC_SAMPLES, start=1):
        print(f"\n[{verse_idx}] VERSE: {verse}")

        data = json.loads(analyze_verse(verse))
        slp1 = data["canonical_slp1"]
        syllables = data["syllables"]
        metrical_pattern = data.get("metrical_pattern", "")
        chanda_name = data.get("chanda", {}).get("name", "unknown")

        _assert_syllable_shape(syllables)

        accents = identify_accents(slp1, syllables)
        _validate_accent_output(syllables, accents)

        pitches = map_pitch_duration(syllables, accents, tempo_bpm=72)
        _validate_pitch_output(syllables, pitches)
        _check_f0_smoothness(pitches)

        # Select and apply raga constraints
        raga = select_raga(chanda_name)
        raga_name = list(raga.values())[0] if isinstance(raga, dict) else "Unknown"
        pitches_snapped = constrain_to_raga(pitches, raga)
        _validate_raga_snapping(pitches, pitches_snapped)
        
        # Generate MIDI
        midi_notes = generate_midi(pitches_snapped)
        _validate_midi_output(syllables, midi_notes)
        
        # Generate explanation
        explanation = explain_melodic_choice(raga, pitches_snapped)
        
        syllable_list = [s["syllable"] for s in syllables]
        accent_codes = [a["accent_code"] for a in accents]
        f0_contour = [p["f0_hz"] for p in pitches]
        f0_snapped = [p["f0_hz"] for p in pitches_snapped]
        duration_list = [p["duration_ms"] for p in pitches]

        print(f"SLP1: {slp1}")
        print(f"Chanda: {chanda_name}")
        print(f"Selected Raga: {raga_name}")
        print(f"Syllables: {syllable_list}")
        print(f"Accent Codes: {accent_codes}")
        print(f"F0 Contour (Hz): {[f'{f:.1f}' for f in f0_contour]}")
        print(f"F0 Snapped (Hz): {[f'{f:.1f}' for f in f0_snapped]}")
        print(f"MIDI Notes: {midi_notes}")
        print(f"Durations (ms): {[f'{d:.2f}' for d in duration_list]}")
        print(f"\nExplanation (Preview):")
        explanation_lines = explanation["explanation"].split("\n")
        for line in explanation_lines[:3]:
            print(f"  {line}")
        if len(explanation_lines) > 3:
            print(f"  ... [+ {len(explanation_lines) - 3} more lines]")

    print("\n" + "=" * 80)
    print("✅ All integration checks PASSED")
    print("=" * 80)

if __name__ == "__main__":
    run_integration_harness()