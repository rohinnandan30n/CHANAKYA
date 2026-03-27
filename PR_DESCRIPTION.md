# Pull Request: feature/dev3 → main

## Title
`[Dev 3] Neural Audio Engine — G2P, Sandhi, Vocoder, Exporter & Pipeline`

---

## Summary

This PR delivers the complete **Dev 3 (Neural Audio Engineer)** contribution to Svara-Chanda. All 7 modules are implemented, tested, and documented. Dev 4 can integrate today with a single import.

---

## What's Included

### New files — `backend/audio/`

| File | Description |
|---|---|
| `sandhi_processor.py` | Applies Sanskrit sandhi rules to SLP1 token lists before G2P |
| `g2p_converter.py` | Grapheme-to-Phoneme conversion (rule-based fallback for Python 3.14) |
| `vocoder.py` | `SanskritVocoder` class — HiFi-GAN wrapper with sine-wave fallback |
| `audio_exporter.py` | Normalises, silence-trims, and exports audio (WAV/MP3) via pydub |
| `finetune_vocoder.py` | HiFi-GAN fine-tuning pipeline — runs in demo mode without torch |
| `audio_pipeline.py` | **Dev 4's single import point** — orchestrates all sub-modules |
| `generate_demo_wav.py` | Pure stdlib WAV generator — zero extra deps, works in any env |
| `README.md` | Full module reference, architecture diagram, and Dev 4 integration guide |

### New files — `backend/tests/`

| File | Description |
|---|---|
| `test_audio_modules.py` | 21+ pytest tests (≥ 3 per module) + end-to-end integration smoke test |
| `conftest.py` | sys.path setup for pytest regardless of invocation directory |

---

## Dev 4 Integration Contract

```python
from backend.audio.audio_pipeline import AudioPipeline

pipeline = AudioPipeline()
result   = pipeline.run(slp1_tokens, f0_hz, durations_ms)
# {
#   "path":         "output/recitation.wav",
#   "duration_sec": 3.14,
#   "sample_rate":  22050,
#   "phonemes":     ["r", "aː", "m", "a", …]
# }
```

No other imports from `backend/audio/` are required by Dev 4. The `AudioPipeline` class handles all internal wiring.

---

## Python 3.14 Compatibility

`torch` and `mlphon` are **not installed** due to Python 3.14 incompatibility. All affected modules operate in verified fallback/demo modes:

- **`vocoder.py`** → sine-wave synthesis (fully audible, correctly timed)
- **`g2p_converter.py`** → rule-based lookup table (covers core Sanskrit phonemes)
- **`finetune_vocoder.py`** → dry-run / corpus validation mode

These fallbacks produce real, usable audio output for the hackathon demo.

---

## Testing

```bash
cd ~/CHANAKYA_dev3 && source venv/bin/activate
pytest backend/tests/test_audio_modules.py -v
```

All 21+ tests pass. Coverage includes:
- Unit tests for each of the 7 modules
- Edge cases: empty input, single tokens, missing checkpoints
- API contract verification for Dev 4
- End-to-end integration smoke test (SLP1 → WAV on disk)

---

## Checklist

- [x] All 7 modules implemented and manually smoke-tested
- [x] pytest suite with ≥ 3 tests per module
- [x] `backend/audio/README.md` written for Dev 4
- [x] No breaking changes to existing project structure
- [x] Branch is up-to-date with `main` (rebase before merging)
- [x] `pydub`, `soundfile`, `numpy`, `ffmpeg` dependencies documented
- [x] Works with Python 3.14 (no torch/mlphon required at runtime)

---

## How to Review

1. Pull the branch: `git fetch origin feature/dev3 && git checkout feature/dev3`
2. Activate venv: `source venv/bin/activate`
3. Run tests: `pytest backend/tests/test_audio_modules.py -v`
4. Skim `backend/audio/README.md` to understand module contracts
5. Try the demo: `python backend/audio/generate_demo_wav.py`

---

## Notes for Merge

- **Merge strategy:** Squash merge preferred to keep `main` history clean
- **After merge:** Dev 4 should delete `feature/dev3` and pull `main`
- **Post-hackathon:** Replace sine-wave vocoder with HiFi-GAN once a Python 3.10/3.11 env is available

---

*Submitted by Dev 3 · Svara-Chanda Hackathon 2025*
