"""
audio_pipeline.py — Svara-Chanda Dev 3 Public Interface
========================================================
This is the single import point Dev 4's orchestrator should use.

Usage (from Dev 4's run_pipeline):
    from backend.audio.audio_pipeline import AudioPipeline

    pipeline = AudioPipeline()
    result = pipeline.run(
        slp1_tokens=["rAma", "iti"],    # from Dev 1
        f0_hz=[220.0, 260.0, 240.0],    # from Dev 2
        durations_ms=[200.0, 150.0, 180.0],  # from Dev 2
        output_path="output/recitation.wav",
        output_format="wav",
    )
    # result = {"path": str, "duration_sec": float, "sample_rate": int, "phonemes": [...]}
"""

import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class AudioPipeline:
    """
    Dev 3's public interface for the Svara-Chanda audio synthesis pipeline.

    Wires together:
        SandhiProcessor  → apply_sandhi()
        G2PConverter     → convert()
        SanskritVocoder  → synthesize()
        AudioExporter    → generate_audio()

    All heavy imports are deferred so Dev 4 can import this module
    even if optional deps (torch, mlphon) are absent.
    """

    def __init__(self, vocoder_checkpoint: Optional[str] = None, device: str = "cpu"):
        self.vocoder_checkpoint = vocoder_checkpoint or ""
        self.device = device
        self._sandhi = None
        self._g2p = None
        self._vocoder = None
        self._exporter = None

    # ------------------------------------------------------------------
    # Lazy loaders
    # ------------------------------------------------------------------

    def _get_sandhi(self):
        if self._sandhi is None:
            from backend.audio.sandhi_processor import SandhiProcessor
            self._sandhi = SandhiProcessor()
        return self._sandhi

    def _get_g2p(self):
        if self._g2p is None:
            from backend.audio.g2p_converter import G2PConverter
            self._g2p = G2PConverter()
        return self._g2p

    def _get_vocoder(self):
        if self._vocoder is None:
            from backend.audio.vocoder import SanskritVocoder
            self._vocoder = SanskritVocoder(
                checkpoint_path=self.vocoder_checkpoint,
                device=self.device,
            )
        return self._vocoder

    def _get_exporter(self):
        if self._exporter is None:
            from backend.audio.audio_exporter import AudioExporter
            self._exporter = AudioExporter(vocoder=self._get_vocoder())
        return self._exporter

    # ------------------------------------------------------------------
    # Main entry point — Dev 4 calls this
    # ------------------------------------------------------------------

    def run(
        self,
        slp1_tokens: List[str],
        f0_hz: List[float],
        durations_ms: List[float],
        output_path: str = "output/recitation.wav",
        output_format: str = "wav",
    ) -> dict:
        """
        Full Dev 3 pipeline: tokens → sandhi → G2P → synthesize → export.

        Args:
            slp1_tokens:   List of SLP1 words from Dev 1
            f0_hz:         Per-phoneme F0 values from Dev 2
            durations_ms:  Per-phoneme durations from Dev 2
            output_path:   Where to write the audio file
            output_format: 'wav' or 'mp3'

        Returns:
            {
                "path": str,            # absolute path to audio file
                "duration_sec": float,
                "sample_rate": int,
                "phonemes": List[str],  # phoneme sequence used
            }
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Stage 1: Sandhi
        logger.info("[Dev3] Stage 1/3: applying sandhi to %d tokens", len(slp1_tokens))
        sandhi_text = self._get_sandhi().apply_sandhi(slp1_tokens)

        # Stage 2: G2P
        logger.info("[Dev3] Stage 2/3: G2P conversion")
        phonemes = self._get_g2p().convert(sandhi_text)
        logger.info("[Dev3] Phonemes: %s", phonemes)

        # Align F0/durations to phoneme count (pad or truncate)
        n = len(phonemes)
        f0_aligned = _align_list(f0_hz, n, default=220.0)
        dur_aligned = _align_list(durations_ms, n, default=150.0)

        # Stage 3: Export
        logger.info("[Dev3] Stage 3/3: synthesizing & exporting audio")
        result = self._get_exporter().generate_audio(
            phonemes=phonemes,
            f0_hz=f0_aligned,
            durations_ms=dur_aligned,
            output_format=output_format,
            output_path=output_path,
        )
        result["phonemes"] = phonemes
        return result

    # ------------------------------------------------------------------
    # Convenience: generate demo WAV with no external inputs
    # ------------------------------------------------------------------

    def generate_demo(self, output_path: str = "output/demo_namaste.wav") -> dict:
        """
        Generate a demo WAV for 'namasté' (namaste in SLP1: 'namas te').
        No Dev 1/2 data needed — uses hardcoded values.
        Safe to call in Python 3.14 / no-torch environments (sine fallback).
        """
        return self.run(
            slp1_tokens=["namas", "te"],
            f0_hz=[220.0, 240.0, 260.0, 250.0, 230.0],
            durations_ms=[200.0, 180.0, 160.0, 180.0, 200.0],
            output_path=output_path,
            output_format="wav",
        )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _align_list(values: List[float], target_len: int, default: float) -> List[float]:
    """Pad with default or truncate a list to target_len."""
    if len(values) >= target_len:
        return values[:target_len]
    return values + [default] * (target_len - len(values))
