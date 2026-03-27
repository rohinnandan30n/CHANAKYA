"""
generate_demo_wav.py — Svara-Chanda Dev 3 Demo Audio Generator
==============================================================
Generates a demo WAV file using ONLY the sine-wave fallback vocoder.
No torch, no mlphon, no GPU needed. Works on Python 3.14.

Run:
    python generate_demo_wav.py
    python generate_demo_wav.py --output output/my_demo.wav --verse "rAma iti"
"""

import argparse
import logging
import math
import struct
import wave
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("demo_wav")

SAMPLE_RATE = 22050


# ---------------------------------------------------------------------------
# Pure-Python sine wave synthesizer (no deps beyond stdlib)
# ---------------------------------------------------------------------------

# Sanskrit phoneme → approximate F0 (Hz) mapping
# Based on Vedic accent levels: udatta~280, svarita~220, anudatta~170
PHONEME_F0 = {
    "n": 220.0, "a": 260.0, "m": 220.0, "s": 180.0,
    "t": 240.0, "e": 280.0, "NA": 220.0, "MA": 250.0,
    "ste": 270.0, "na": 240.0, "mas": 220.0,
}
DEFAULT_F0 = 220.0
DEFAULT_DUR_MS = 180.0


def sine_wave(f0: float, duration_ms: float, sample_rate: int = SAMPLE_RATE,
              amplitude: float = 0.4) -> list:
    """Generate a single sine tone as a list of float samples."""
    n_samples = int(sample_rate * duration_ms / 1000.0)
    return [
        amplitude * math.sin(2 * math.pi * f0 * i / sample_rate)
        for i in range(n_samples)
    ]


def apply_envelope(samples: list, attack_ms: float = 10.0, release_ms: float = 20.0,
                   sample_rate: int = SAMPLE_RATE) -> list:
    """Apply simple linear attack/release envelope to reduce clicks."""
    n = len(samples)
    attack_n = min(int(sample_rate * attack_ms / 1000.0), n // 4)
    release_n = min(int(sample_rate * release_ms / 1000.0), n // 4)
    result = list(samples)
    for i in range(attack_n):
        result[i] *= i / attack_n
    for i in range(release_n):
        result[n - 1 - i] *= i / release_n
    return result


def normalize(samples: list, target_peak: float = 0.85) -> list:
    """Normalize to target peak amplitude."""
    peak = max(abs(s) for s in samples) if samples else 1.0
    if peak < 1e-6:
        return samples
    scale = target_peak / peak
    return [s * scale for s in samples]


def samples_to_wav(samples: list, path: str, sample_rate: int = SAMPLE_RATE):
    """Write float samples to a WAV file (16-bit PCM)."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    int_samples = [max(-32768, min(32767, int(s * 32767))) for s in samples]
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(int_samples)}h", *int_samples))


def synthesize_verse(verse_slp1: str) -> list:
    """
    Convert a SLP1 verse string into audio samples using sine fallback.
    Each 'syllable' (space-split token) gets its own tone segment.
    """
    tokens = verse_slp1.strip().split()
    all_samples = []

    # Brief silence at start
    all_samples.extend([0.0] * int(SAMPLE_RATE * 0.1))

    for token in tokens:
        # Derive F0 from token (use last char if not in table)
        f0 = PHONEME_F0.get(token, PHONEME_F0.get(token[-1] if token else "a", DEFAULT_F0))
        dur = DEFAULT_DUR_MS * (1.5 if len(token) > 3 else 1.0)  # longer tokens = longer

        seg = sine_wave(f0, dur)
        seg = apply_envelope(seg)
        all_samples.extend(seg)

        # Short inter-syllable gap
        all_samples.extend([0.0] * int(SAMPLE_RATE * 0.04))

    # Brief silence at end
    all_samples.extend([0.0] * int(SAMPLE_RATE * 0.15))

    return normalize(all_samples)


# ---------------------------------------------------------------------------
# Verse definitions
# ---------------------------------------------------------------------------

DEMO_VERSES = {
    "namaste": "namas te",
    "gayatri": "tat savitur vareNyaM Bargo devasya DImahi",
    "shanti": "oM SAntih SAntih SAntih",
    "mangala": "sarveSAM svastir Bavatu sarveSAM SAntir Bavatu",
}


def generate_demo_wav(output_path: str = "output/demo_namaste.wav",
                      verse_key: str = "namaste",
                      custom_verse: str = "") -> dict:
    """
    Generate a demo WAV. Returns metadata dict.
    """
    verse = custom_verse.strip() if custom_verse else DEMO_VERSES.get(verse_key, DEMO_VERSES["namaste"])
    logger.info("Synthesizing verse: '%s'", verse)

    samples = synthesize_verse(verse)
    samples_to_wav(samples, output_path)

    duration_sec = len(samples) / SAMPLE_RATE
    logger.info("Demo WAV saved → %s (%.2f sec, %d samples)", output_path, duration_sec, len(samples))

    return {
        "path": str(Path(output_path).resolve()),
        "duration_sec": round(duration_sec, 3),
        "sample_rate": SAMPLE_RATE,
        "verse": verse,
        "format": "wav",
        "note": "Sine-wave fallback (no torch). Real neural synthesis needs torch+HiFi-GAN.",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate Svara-Chanda demo WAV (sine fallback)")
    parser.add_argument("--output", default="output/demo_namaste.wav", help="Output WAV path")
    parser.add_argument(
        "--verse",
        choices=list(DEMO_VERSES.keys()),
        default="namaste",
        help="Preset verse to synthesize",
    )
    parser.add_argument("--custom_verse", default="", help="Custom SLP1 verse (overrides --verse)")
    parser.add_argument("--all", action="store_true", help="Generate all preset verses")
    args = parser.parse_args()

    if args.all:
        for key, verse in DEMO_VERSES.items():
            out = f"output/demo_{key}.wav"
            result = generate_demo_wav(out, verse_key=key)
            print(f"✓ {key}: {result['path']} ({result['duration_sec']}s)")
    else:
        result = generate_demo_wav(
            output_path=args.output,
            verse_key=args.verse,
            custom_verse=args.custom_verse,
        )
        print("\n=== Demo WAV Generated ===")
        for k, v in result.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
