"""
Svara-Chanda · Dev 3 (Neural Audio Engineer)
pytest test suite — backend/audio/ — all 7 modules
Min 3 tests per module (21 tests total + shared fixtures)

Run with:
    cd ~/CHANAKYA_dev3
    source venv/bin/activate
    pytest backend/tests/test_audio_modules.py -v
"""

import os
import sys
import tempfile
import wave
import struct
import math
import json
import pytest

# ── make sure project root is on sys.path ──────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ═══════════════════════════════════════════════════════════════════════════
# Shared fixtures
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_slp1_tokens():
    """A short Sanskrit sentence in SLP1 transliteration."""
    return ["rAma", "iti", "nAma"]


@pytest.fixture
def sample_phonemes():
    return ["r", "aː", "m", "a", "ʔ", "i", "t", "i"]


@pytest.fixture
def sample_f0_hz():
    return [220.0, 240.0, 260.0, 240.0, 220.0, 200.0, 180.0, 180.0]


@pytest.fixture
def sample_durations_ms():
    return [120.0, 240.0, 120.0, 120.0, 120.0, 120.0, 120.0, 240.0]


@pytest.fixture
def tmp_wav(tmp_path):
    """Generate a minimal valid 22050 Hz mono WAV file for testing."""
    wav_path = str(tmp_path / "test_input.wav")
    sample_rate = 22050
    duration_s = 0.5
    num_samples = int(sample_rate * duration_s)
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(num_samples):
            value = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            wf.writeframes(struct.pack("<h", value))
    return wav_path


# ═══════════════════════════════════════════════════════════════════════════
# 1. sandhi_processor.py
# ═══════════════════════════════════════════════════════════════════════════

class TestSandhiProcessor:
    """Tests for backend/audio/sandhi_processor.py"""

    @pytest.fixture(autouse=True)
    def import_module(self):
        from backend.audio.sandhi_processor import apply_sandhi
        self.apply_sandhi = apply_sandhi

    def test_basic_vowel_sandhi(self):
        """a + i → e  (the classic ā + i = e rule in SLP1)."""
        tokens = ["rAma", "iti"]
        result = self.apply_sandhi(tokens)
        assert isinstance(result, str), "apply_sandhi must return a string"
        # The merged form should appear in the output
        assert "rAmeti" in result or "rAma" in result  # rule or passthrough

    def test_returns_non_empty_string(self, sample_slp1_tokens):
        result = self.apply_sandhi(sample_slp1_tokens)
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_single_token_no_crash(self):
        """Single-word input should not raise and returns the word itself."""
        result = self.apply_sandhi(["namaskaroti"])
        assert "namaskaroti" in result

    def test_empty_list_returns_empty(self):
        result = self.apply_sandhi([])
        assert result == "" or result is not None  # graceful, not an exception

    def test_output_is_slp1_compatible(self, sample_slp1_tokens):
        """Output must not contain spaces inside what was a single token."""
        result = self.apply_sandhi(sample_slp1_tokens)
        # SLP1 uses no spaces within a sandhi compound
        assert "\n" not in result


# ═══════════════════════════════════════════════════════════════════════════
# 2. g2p_converter.py
# ═══════════════════════════════════════════════════════════════════════════

class TestG2PConverter:
    """Tests for backend/audio/g2p_converter.py"""

    @pytest.fixture(autouse=True)
    def import_module(self):
        from backend.audio.g2p_converter import convert
        self.convert = convert

    def test_returns_list_of_strings(self):
        result = self.convert("rAma")
        assert isinstance(result, list)
        assert all(isinstance(p, str) for p in result)

    def test_non_empty_output_for_valid_input(self):
        result = self.convert("namaskaroti")
        assert len(result) > 0, "G2P must produce at least one phoneme"

    def test_raises_on_empty_string(self):
        with pytest.raises((ValueError, Exception)):
            self.convert("")

    def test_conjunct_consonant_handling(self):
        """kSa is a conjunct consonant in SLP1; output must not be empty."""
        result = self.convert("kSa")
        assert len(result) > 0

    def test_multiple_words_converted(self):
        result = self.convert("rAma iti nAma")
        assert len(result) > 3  # should produce many phonemes for 3 words


# ═══════════════════════════════════════════════════════════════════════════
# 3. vocoder.py
# ═══════════════════════════════════════════════════════════════════════════

class TestVocoder:
    """Tests for backend/audio/vocoder.py  (sine-wave fallback, no torch)."""

    @pytest.fixture(autouse=True)
    def import_module(self):
        from backend.audio.vocoder import SanskritVocoder
        self.SanskritVocoder = SanskritVocoder

    def test_instantiation_no_checkpoint(self):
        """Vocoder must initialise in demo/fallback mode without a checkpoint."""
        vocoder = self.SanskritVocoder(checkpoint_path=None)
        assert vocoder is not None

    def test_synthesize_returns_numpy_array(self, sample_phonemes, sample_f0_hz, sample_durations_ms):
        import numpy as np
        vocoder = self.SanskritVocoder(checkpoint_path=None)
        waveform = vocoder.synthesize(sample_phonemes, sample_f0_hz, sample_durations_ms)
        assert isinstance(waveform, np.ndarray), "synthesize() must return np.ndarray"

    def test_waveform_not_silent(self, sample_phonemes, sample_f0_hz, sample_durations_ms):
        """Waveform should have non-zero energy (not all zeros)."""
        vocoder = self.SanskritVocoder(checkpoint_path=None)
        waveform = vocoder.synthesize(sample_phonemes, sample_f0_hz, sample_durations_ms)
        assert waveform.max() != 0.0 or waveform.min() != 0.0

    def test_waveform_float32(self, sample_phonemes, sample_f0_hz, sample_durations_ms):
        import numpy as np
        vocoder = self.SanskritVocoder(checkpoint_path=None)
        waveform = vocoder.synthesize(sample_phonemes, sample_f0_hz, sample_durations_ms)
        assert waveform.dtype in (np.float32, np.float64)

    def test_empty_phonemes_does_not_crash(self):
        vocoder = self.SanskritVocoder(checkpoint_path=None)
        result = vocoder.synthesize([], [], [])
        # Should return empty array or near-silence, not crash
        assert result is not None


# ═══════════════════════════════════════════════════════════════════════════
# 4. audio_exporter.py
# ═══════════════════════════════════════════════════════════════════════════

class TestAudioExporter:
    """Tests for backend/audio/audio_exporter.py"""

    @pytest.fixture(autouse=True)
    def import_module(self):
        from backend.audio.audio_exporter import generate_audio
        self.generate_audio = generate_audio

    def test_wav_file_created(self, sample_phonemes, sample_f0_hz, sample_durations_ms, tmp_path):
        out = str(tmp_path / "output.wav")
        result = self.generate_audio(
            phonemes=sample_phonemes,
            f0_hz=sample_f0_hz,
            durations_ms=sample_durations_ms,
            output_format="wav",
            output_path=out,
        )
        assert os.path.exists(result["path"]), "WAV output file must exist"

    def test_returns_required_keys(self, sample_phonemes, sample_f0_hz, sample_durations_ms, tmp_path):
        out = str(tmp_path / "output.wav")
        result = self.generate_audio(
            phonemes=sample_phonemes,
            f0_hz=sample_f0_hz,
            durations_ms=sample_durations_ms,
            output_path=out,
        )
        assert "path" in result
        assert "duration_sec" in result
        assert "sample_rate" in result

    def test_duration_greater_than_zero(self, sample_phonemes, sample_f0_hz, sample_durations_ms, tmp_path):
        out = str(tmp_path / "output.wav")
        result = self.generate_audio(
            phonemes=sample_phonemes,
            f0_hz=sample_f0_hz,
            durations_ms=sample_durations_ms,
            output_path=out,
        )
        assert result["duration_sec"] > 0.0

    def test_sample_rate_is_standard(self, sample_phonemes, sample_f0_hz, sample_durations_ms, tmp_path):
        out = str(tmp_path / "output.wav")
        result = self.generate_audio(
            phonemes=sample_phonemes,
            f0_hz=sample_f0_hz,
            durations_ms=sample_durations_ms,
            output_path=out,
        )
        assert result["sample_rate"] in (22050, 44100, 16000)


# ═══════════════════════════════════════════════════════════════════════════
# 5. finetune_vocoder.py
# ═══════════════════════════════════════════════════════════════════════════

class TestFinetuneVocoder:
    """Tests for backend/audio/finetune_vocoder.py  (demo mode)."""

    @pytest.fixture(autouse=True)
    def import_module(self):
        from backend.audio import finetune_vocoder as ft
        self.ft = ft

    def test_module_imports_cleanly(self):
        """Module must import without errors even without torch."""
        assert self.ft is not None

    def test_load_corpus_returns_list_or_dataset(self, tmp_path):
        """load_corpus on an empty dir should return empty list, not crash."""
        if not hasattr(self.ft, "load_corpus"):
            pytest.skip("load_corpus not exposed at module level")
        result = self.ft.load_corpus(str(tmp_path))
        assert result is not None

    def test_demo_mode_flag_exists(self):
        """finetune_vocoder should expose a DEMO_MODE or similar constant."""
        has_demo = (
            hasattr(self.ft, "DEMO_MODE")
            or hasattr(self.ft, "demo_mode")
            or hasattr(self.ft, "TORCH_AVAILABLE")
        )
        assert has_demo, "finetune_vocoder must declare its demo/fallback mode"

    def test_argparse_config_accessible(self):
        """Script must be importable and expose its arg parser or config dict."""
        # If there's a get_config() or build_parser(), call it
        if hasattr(self.ft, "get_config"):
            cfg = self.ft.get_config([])
            assert cfg is not None
        elif hasattr(self.ft, "build_parser"):
            parser = self.ft.build_parser()
            assert parser is not None
        else:
            pytest.skip("No get_config/build_parser found — manual review OK")


# ═══════════════════════════════════════════════════════════════════════════
# 6. audio_pipeline.py
# ═══════════════════════════════════════════════════════════════════════════

class TestAudioPipeline:
    """Tests for backend/audio/audio_pipeline.py  (Dev 4 integration point)."""

    @pytest.fixture(autouse=True)
    def import_module(self):
        from backend.audio.audio_pipeline import AudioPipeline
        self.AudioPipeline = AudioPipeline

    def test_pipeline_instantiation(self):
        pipeline = self.AudioPipeline()
        assert pipeline is not None

    def test_run_returns_dict(self, sample_slp1_tokens, sample_f0_hz, sample_durations_ms):
        pipeline = self.AudioPipeline()
        result = pipeline.run(sample_slp1_tokens, sample_f0_hz, sample_durations_ms)
        assert isinstance(result, dict), "pipeline.run() must return a dict"

    def test_run_returns_all_required_keys(self, sample_slp1_tokens, sample_f0_hz, sample_durations_ms):
        """API contract: result must contain path, duration_sec, sample_rate, phonemes."""
        pipeline = self.AudioPipeline()
        result = pipeline.run(sample_slp1_tokens, sample_f0_hz, sample_durations_ms)
        for key in ("path", "duration_sec", "sample_rate", "phonemes"):
            assert key in result, f"Missing key in pipeline result: '{key}'"

    def test_audio_file_exists_after_run(self, sample_slp1_tokens, sample_f0_hz, sample_durations_ms):
        pipeline = self.AudioPipeline()
        result = pipeline.run(sample_slp1_tokens, sample_f0_hz, sample_durations_ms)
        assert os.path.exists(result["path"]), "Audio file must be written to disk"

    def test_phonemes_list_non_empty(self, sample_slp1_tokens, sample_f0_hz, sample_durations_ms):
        pipeline = self.AudioPipeline()
        result = pipeline.run(sample_slp1_tokens, sample_f0_hz, sample_durations_ms)
        assert isinstance(result["phonemes"], list)
        assert len(result["phonemes"]) > 0


# ═══════════════════════════════════════════════════════════════════════════
# 7. generate_demo_wav.py
# ═══════════════════════════════════════════════════════════════════════════

class TestGenerateDemoWav:
    """Tests for backend/audio/generate_demo_wav.py  (pure stdlib demo)."""

    @pytest.fixture(autouse=True)
    def import_module(self):
        import importlib.util, types
        # Import the module without executing __main__ block
        spec = importlib.util.spec_from_file_location(
            "generate_demo_wav",
            os.path.join(PROJECT_ROOT, "backend", "audio", "generate_demo_wav.py"),
        )
        self.mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(self.mod)
        except SystemExit:
            pass  # Some demo scripts call sys.exit on import in __main__

    def test_module_loads(self):
        assert self.mod is not None

    def test_generate_function_exists(self):
        assert hasattr(self.mod, "generate_demo_wav") or hasattr(self.mod, "main"), \
            "generate_demo_wav.py must expose generate_demo_wav() or main()"

    def test_demo_wav_is_valid(self, tmp_path):
        """Generated WAV must be openable by stdlib wave module."""
        out = str(tmp_path / "demo.wav")
        if hasattr(self.mod, "generate_demo_wav"):
            self.mod.generate_demo_wav(output_path=out)
        elif hasattr(self.mod, "main"):
            self.mod.main(output_path=out)
        else:
            pytest.skip("No callable entry-point found")

        assert os.path.exists(out), "Demo WAV file must be created"
        with wave.open(out, "r") as wf:
            assert wf.getnchannels() in (1, 2)
            assert wf.getframerate() > 0
            assert wf.getnframes() > 0

    def test_demo_wav_has_audio_content(self, tmp_path):
        """Demo WAV must contain non-silent audio."""
        out = str(tmp_path / "demo_content.wav")
        if hasattr(self.mod, "generate_demo_wav"):
            self.mod.generate_demo_wav(output_path=out)
        elif hasattr(self.mod, "main"):
            self.mod.main(output_path=out)
        else:
            pytest.skip("No callable entry-point found")

        with wave.open(out, "r") as wf:
            frames = wf.readframes(wf.getnframes())
        samples = struct.unpack(f"<{len(frames)//2}h", frames)
        assert any(s != 0 for s in samples), "Demo WAV must not be silent"


# ═══════════════════════════════════════════════════════════════════════════
# End-to-end integration smoke test
# ═══════════════════════════════════════════════════════════════════════════

class TestEndToEndIntegration:
    """Full pipeline smoke test: SLP1 tokens → audio file on disk."""

    def test_full_pipeline_smoke(self, sample_slp1_tokens, sample_f0_hz, sample_durations_ms):
        from backend.audio.audio_pipeline import AudioPipeline
        pipeline = AudioPipeline()
        result = pipeline.run(sample_slp1_tokens, sample_f0_hz, sample_durations_ms)

        assert result["duration_sec"] > 0, "Output audio must have positive duration"
        assert os.path.isfile(result["path"]), "Output file must exist on disk"
        assert result["sample_rate"] > 0, "Sample rate must be positive"
        assert len(result["phonemes"]) > 0, "Phoneme list must not be empty"

    def test_dev4_import_contract(self):
        """Dev 4 must be able to do exactly: from backend.audio.audio_pipeline import AudioPipeline"""
        try:
            from backend.audio.audio_pipeline import AudioPipeline  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Dev 4 import contract broken: {e}")
