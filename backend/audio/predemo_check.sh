#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# Svara-Chanda · Dev 3 · Pre-demo validation script
# Run this before the hackathon demo to confirm everything is green.
#
# Usage:
#   cd ~/CHANAKYA_dev3
#   source venv/bin/activate
#   bash backend/audio/predemo_check.sh
# ─────────────────────────────────────────────────────────────────────────

set -e
PASS=0
FAIL=0
WARN=0

print_ok()   { echo "  ✅  $1"; ((PASS++)); }
print_fail() { echo "  ❌  $1"; ((FAIL++)); }
print_warn() { echo "  ⚠️   $1"; ((WARN++)); }

echo ""
echo "══════════════════════════════════════════"
echo "  Svara-Chanda · Dev 3 · Pre-demo Check  "
echo "══════════════════════════════════════════"
echo ""

# ── 1. Python version ──────────────────────────────────────────────────────
echo "▶ Environment"
PYVER=$(python --version 2>&1)
echo "  Python: $PYVER"

# ── 2. Required packages ───────────────────────────────────────────────────
for pkg in pydub soundfile numpy; do
  if python3 -c "import $pkg" 2>/dev/null; then
    print_ok "$pkg importable"
  else
    print_warn "$pkg NOT importable — run: pip install $pkg"
  fi
done

# torch is optional (demo mode)
if python3 -c "import torch" 2>/dev/null; then
  print_ok "torch available (full neural mode)"
else
  print_warn "torch NOT available — vocoder runs in sine-wave demo mode (OK for hackathon)"
fi

# ffmpeg for MP3
if command -v ffmpeg &>/dev/null; then
  print_ok "ffmpeg on PATH (MP3 export enabled)"
else
  print_warn "ffmpeg NOT on PATH — WAV output only (MP3 export disabled)"
fi

echo ""
echo "▶ Module imports"

MODULES=(
  "backend.audio.sandhi_processor"
  "backend.audio.g2p_converter"
  "backend.audio.vocoder"
  "backend.audio.audio_exporter"
  "backend.audio.finetune_vocoder"
  "backend.audio.audio_pipeline"
  "backend.audio.generate_demo_wav"
)

for mod in "${MODULES[@]}"; do
  if python3 -c "import $mod" 2>/dev/null; then
    print_ok "$mod"
  else
    print_fail "$mod — IMPORT ERROR"
  fi
done

echo ""
echo "▶ Dev 4 import contract"
if python -c "from backend.audio.audio_pipeline import AudioPipeline" 2>/dev/null; then
  print_ok "from backend.audio.audio_pipeline import AudioPipeline"
else
  print_fail "Dev 4 import contract BROKEN"
fi

echo ""
echo "▶ pytest suite"
if pytest backend/tests/test_audio_modules.py -q --tb=no 2>/dev/null; then
  print_ok "All tests passing"
else
  print_fail "Some tests FAILED — run: pytest backend/tests/test_audio_modules.py -v"
fi

echo ""
echo "▶ Demo WAV generation"
mkdir -p output
if python backend/audio/generate_demo_wav.py --out output/predemo_check.wav 2>/dev/null; then
  if [ -f output/predemo_check.wav ]; then
    SIZE=$(wc -c < output/predemo_check.wav)
    print_ok "Demo WAV created (${SIZE} bytes) → output/predemo_check.wav"
  else
    print_fail "generate_demo_wav.py ran but no file created"
  fi
else
  print_fail "generate_demo_wav.py failed"
fi

echo ""
echo "▶ Full pipeline smoke test"
python - <<'PYEOF'
import sys, os
sys.path.insert(0, os.getcwd())
try:
    from backend.audio.audio_pipeline import AudioPipeline
    pipeline = AudioPipeline()
    result = pipeline.run(
        slp1_tokens   = ["rAma", "iti", "nAma"],
        f0_hz         = [220.0, 240.0, 260.0],
        durations_ms  = [120.0, 240.0, 120.0],
    )
    assert "path" in result and "duration_sec" in result
    assert result["duration_sec"] > 0
    assert os.path.isfile(result["path"])
    print("  ✅  AudioPipeline.run() → " + str(result))
    sys.exit(0)
except Exception as e:
    print("  ❌  Pipeline smoke test FAILED: " + str(e))
    sys.exit(1)
PYEOF
PIPELINE_EXIT=$?
if [ $PIPELINE_EXIT -ne 0 ]; then ((FAIL++)); else ((PASS++)); fi

# ── Summary ────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo "  Results: ✅ $PASS passed  ⚠️  $WARN warnings  ❌ $FAIL failed"
echo "══════════════════════════════════════════"
echo ""

if [ $FAIL -gt 0 ]; then
  echo "  ‼️  Fix the $FAIL failure(s) before the demo!"
  exit 1
else
  echo "  🎉  All checks passed — ready for demo!"
  exit 0
fi
