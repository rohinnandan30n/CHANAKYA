# backend/audio/ — Dev 3: Neural Audio Engine

> **Svara-Chanda · Hackathon 2025**
> Owner: Dev 3 (Neural Audio Engineer) · Branch: `feature/dev3`

---

## Overview

This package converts SLP1 Sanskrit tokens + melodic data (F0 contours, durations) produced by Dev 2 into a rendered WAV audio file. It is **Dev 4's single integration point**: import `AudioPipeline` and call `.run()`.

```python
from backend.audio.audio_pipeline import AudioPipeline

pipeline = AudioPipeline()
result   = pipeline.run(slp1_tokens, f0_hz, durations_ms)
# result → {"path": str, "duration_sec": float, "sample_rate": int, "phonemes": list[str]}
```

---

## Module Reference

### `audio_pipeline.py` ← **Dev 4 starts here**

The single public façade for the entire audio subsystem.

| Symbol | Signature | Description |
|---|---|---|
| `AudioPipeline` | `__init__(self)` | Instantiates all sub-modules |
| | `run(slp1_tokens, f0_hz, durations_ms) → dict` | Full synthesis pipeline |

**Return dict schema:**

```json
{
  "path":         "output/recitation.wav",   // absolute or relative path to audio file
  "duration_sec": 3.14,                       // float, seconds
  "sample_rate":  22050,                      // int, Hz
  "phonemes":     ["r", "aː", "m", "a", …]  // list of IPA/SAMPA strings
}
```

**Dev 4 integration checklist:**
- ✅ Import only from `backend.audio.audio_pipeline`
- ✅ Pass `slp1_tokens: list[str]` from Dev 1's canonical SLP1 output
- ✅ Pass `f0_hz: list[float]` and `durations_ms: list[float]` from Dev 2's pitch mapper (one value per phoneme/syllable)
- ✅ Use `result["path"]` to serve the audio file via FastAPI `FileResponse`

---

### `sandhi_processor.py`

Pre-processes SLP1 tokens by applying Sanskrit sandhi rules before phonemisation. This improves G2P accuracy by resolving word-boundary transformations.

```python
from backend.audio.sandhi_processor import apply_sandhi

merged = apply_sandhi(["rAma", "iti"])   # → "rAmeti"
```

| Function | Signature | Notes |
|---|---|---|
| `apply_sandhi` | `(tokens: list[str]) → str` | Applies external & internal sandhi rules |

**Data dependency:** Reads `backend/data/linguistic/sandhi_rules.json`. If the file is absent the function falls back to simple space-joining and logs a warning.

---

### `g2p_converter.py`

Grapheme-to-Phoneme conversion for Sanskrit SLP1 text. Returns a flat list of IPA/SAMPA phoneme strings.

```python
from backend.audio.g2p_converter import convert

phonemes = convert("rAma")   # → ["r", "aː", "m", "a"]
```

| Function | Signature | Notes |
|---|---|---|
| `convert` | `(slp1_text: str) → list[str]` | Raises `ValueError` on empty/non-SLP1 input |

**Fallback behaviour:** Because `mlphon` and `torch` are incompatible with Python 3.14, the converter uses a rule-based lookup table in demo mode. A `G2P_MODE` module constant signals which backend is active (`"neural"` or `"rule_based"`).

---

### `vocoder.py`

Synthesises a waveform from phonemes + F0 + durations. In production this wraps HiFi-GAN; in demo mode it generates a sine-wave approximation so the pipeline runs end-to-end without GPU dependencies.

```python
from backend.audio.vocoder import SanskritVocoder

vocoder  = SanskritVocoder(checkpoint_path=None)          # None → demo mode
waveform = vocoder.synthesize(phonemes, f0_hz, durations_ms)  # → np.ndarray float32 @ 22050 Hz
```

| Class | Method | Returns |
|---|---|---|
| `SanskritVocoder` | `__init__(checkpoint_path, device="cpu")` | — |
| | `synthesize(phonemes, f0_hz, durations_ms) → np.ndarray` | float32 waveform |

**Demo mode:** When `checkpoint_path=None` or when `torch` is unavailable, the vocoder generates sine-wave tones at each F0 value scaled to the given duration. The output is audible and correctly timed — suitable for a hackathon demo.

---

### `audio_exporter.py`

Post-processes the raw waveform (normalisation, silence trimming) and writes the final audio file to disk.

```python
from backend.audio.audio_exporter import generate_audio

result = generate_audio(
    phonemes     = ["r", "aː", "m", "a"],
    f0_hz        = [220.0, 240.0, 240.0, 220.0],
    durations_ms = [120.0, 240.0, 120.0, 120.0],
    output_format = "wav",           # "wav" | "mp3"
    output_path   = "output/recitation.wav",
)
# result → {"path": str, "duration_sec": float, "sample_rate": int}
```

Post-processing chain:
1. Normalise amplitude to −3 dBFS (`pydub`)
2. Trim leading/trailing silence (threshold −40 dBFS)
3. Export to `wav` or `mp3`

---

### `finetune_vocoder.py`

Training/fine-tuning script to adapt HiFi-GAN to Sanskrit phonetics using a local speech corpus. Runs in **demo mode** when `torch` is unavailable (prints a dry-run log instead of training).

```bash
# Full training (requires torch + GPU)
python -m backend.audio.finetune_vocoder --epochs 10 --lr 2e-4 --batch_size 8

# Demo mode (no torch needed — just validates the corpus loader)
python -m backend.audio.finetune_vocoder --demo
```

| CLI arg | Default | Description |
|---|---|---|
| `--epochs` | `10` | Training epochs |
| `--lr` | `2e-4` | Learning rate |
| `--batch_size` | `8` | Batch size |
| `--corpus_dir` | `backend/data/audio/sanskrit_speech_corpus/` | WAV + text pairs |
| `--demo` | `False` | Skip actual training; validate loader only |

Checkpoints saved to `backend/data/models/vocoder/ft_{epoch}.pt`.

---

### `generate_demo_wav.py`

Pure Python stdlib demo WAV generator. **No dependencies** — no pydub, no numpy, no torch. Produces a correctly-structured WAV file for testing the full pipeline on machines with minimal environments (CI, restricted hackathon VMs).

```bash
python backend/audio/generate_demo_wav.py              # writes output/demo.wav
python backend/audio/generate_demo_wav.py --out /tmp/test.wav
```

```python
from backend.audio.generate_demo_wav import generate_demo_wav

generate_demo_wav(output_path="output/demo.wav", duration_s=1.0, freq_hz=440)
```

---

## Installation (Dev 3 environment)

```bash
# Clone and set up
git clone https://github.com/rohinnandan30n/CHANAKYA.git ~/CHANAKYA_dev3
cd ~/CHANAKYA_dev3
git checkout feature/dev3

# Activate venv (already configured)
source venv/bin/activate

# Dependencies (torch NOT installed — Python 3.14 incompatible)
pip install pydub soundfile numpy
# ffmpeg must be on PATH for pydub MP3 export:
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS:         brew install ffmpeg
```

---

## Running the Tests

```bash
cd ~/CHANAKYA_dev3
source venv/bin/activate

# All Dev 3 tests
pytest backend/tests/test_audio_modules.py -v

# With coverage report
pytest backend/tests/test_audio_modules.py -v --tb=short --cov=backend.audio

# Just one module
pytest backend/tests/test_audio_modules.py::TestAudioPipeline -v
```

Expected output: **≥ 21 tests passing** (3 per module × 7 modules).

---

## Architecture Diagram

```
Dev 1 output              Dev 2 output
slp1_tokens: list[str]    f0_hz: list[float]
                          durations_ms: list[float]
        │                         │
        ▼                         │
sandhi_processor.py               │
  apply_sandhi()                  │
        │                         │
        ▼                         │
g2p_converter.py                  │
  convert() → phonemes ───────────┤
                                  │
                                  ▼
                            vocoder.py
                         SanskritVocoder
                           .synthesize()
                           → np.ndarray
                                  │
                                  ▼
                          audio_exporter.py
                           generate_audio()
                           → {path, duration_sec,
                              sample_rate}
                                  │
                                  ▼
                          audio_pipeline.py   ← Dev 4 imports this
                           AudioPipeline
                             .run()
                           → {path, duration_sec,
                              sample_rate, phonemes}
```

---

## Known Limitations (Hackathon Scope)

| Limitation | Impact | Workaround |
|---|---|---|
| `torch` / `mlphon` not installable on Python 3.14 | No neural vocoder or neural G2P | Sine-wave vocoder + rule-based G2P in demo mode |
| No Sanskrit speech corpus bundled | `finetune_vocoder.py` runs in demo mode only | Fine-tuning deferred post-hackathon |
| MP3 export requires `ffmpeg` on PATH | MP3 output may fail in some CI environments | Use WAV (`output_format="wav"`) as default |

---

## Contact / Handoff

- **Dev 3 branch:** `feature/dev3`
- **Integration branch (target):** `main`
- **Dev 4 import contract:** `from backend.audio.audio_pipeline import AudioPipeline`
- Any changes to the return schema of `AudioPipeline.run()` must be coordinated with Dev 4 before merging.
