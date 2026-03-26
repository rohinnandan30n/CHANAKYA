"""
vocoder.py - Dev 3: Neural Audio Engineer
HiFi-GAN vocoder wrapper for Sanskrit TTS.
Accepts F0 (frequencies) and durations from Dev 2's melodic_output.schema.json.

Schema fields used:
  - frequencies: List[float]  (F0 in Hz)
  - durations:   List[float]  (duration per phoneme in ms)
  - notes:       List[str]    (note names, optional)
"""

import logging
import numpy as np
from typing import List, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SAMPLE_RATE = 22050


class SanskritVocoder:
    """
    HiFi-GAN based vocoder for Sanskrit TTS.
    Accepts phonemes + F0 (frequencies) + durations from Dev 2's melodic output.
    """

    def __init__(self, checkpoint_path: str = "backend/data/models/vocoder",
                 device: str = "cpu"):
        self.checkpoint_path = checkpoint_path
        self.device = self._detect_device(device)
        self.model = None
        self.sample_rate = SAMPLE_RATE
        self._load_model()

    def _detect_device(self, requested: str) -> str:
        """Auto-detect CUDA availability."""
        try:
            import torch
            if torch.cuda.is_available():
                logger.debug("CUDA available, using GPU")
                return "cuda"
        except ImportError:
            pass
        logger.debug("Using CPU")
        return "cpu"

    def _load_model(self):
        """Load HiFi-GAN checkpoint if available."""
        try:
            import torch
            import os
            checkpoint_file = f"{self.checkpoint_path}/generator.pt"
            if os.path.exists(checkpoint_file):
                self.model = torch.load(checkpoint_file, map_location=self.device)
                self.model.eval()
                logger.debug(f"HiFi-GAN loaded from {checkpoint_file}")
            else:
                logger.warning(
                    f"No checkpoint at {checkpoint_file}. "
                    "Using rule-based synthesis fallback."
                )
                self.model = None
        except ImportError:
            logger.warning("torch not installed. Using rule-based synthesis fallback.")
            self.model = None

    def _phonemes_to_ids(self, phonemes: List[str]) -> List[int]:
        """Map phonemes to model vocabulary IDs."""
        vocab = {p: i for i, p in enumerate(sorted(set(phonemes)))}
        return [vocab.get(p, 0) for p in phonemes]

    def _rule_based_synthesis(self, phonemes: List[str],
                               f0_hz: List[float],
                               durations_ms: List[float]) -> np.ndarray:
        """
        Lightweight rule-based synthesis fallback when HiFi-GAN is unavailable.
        Generates sine waves at given F0 frequencies.
        """
        logger.debug("Using rule-based sine wave synthesis")
        waveform_parts = []

        n = min(len(phonemes), len(f0_hz), len(durations_ms))

        for i in range(n):
            freq = f0_hz[i] if f0_hz[i] > 0 else 120.0
            dur_samples = int((durations_ms[i] / 1000.0) * self.sample_rate)

            if dur_samples <= 0:
                continue

            t = np.linspace(0, durations_ms[i] / 1000.0, dur_samples, endpoint=False)

            # Sine wave + harmonics for richer sound
            wave = (
                0.5 * np.sin(2 * np.pi * freq * t) +
                0.25 * np.sin(2 * np.pi * freq * 2 * t) +
                0.1 * np.sin(2 * np.pi * freq * 3 * t)
            )

            # Fade in/out to avoid clicks
            fade = min(50, dur_samples // 4)
            wave[:fade] *= np.linspace(0, 1, fade)
            wave[-fade:] *= np.linspace(1, 0, fade)

            waveform_parts.append(wave.astype(np.float32))

        if not waveform_parts:
            return np.zeros(self.sample_rate, dtype=np.float32)

        return np.concatenate(waveform_parts)

    def synthesize(self, phonemes: List[str],
                   f0_hz: List[float],
                   durations_ms: List[float]) -> np.ndarray:
        """
        Synthesize waveform from phonemes + F0 + durations.

        Args:
            phonemes:     List of IPA/SAMPA phoneme strings (from g2p_converter)
            f0_hz:        F0 frequencies in Hz (from Dev 2 melodic output 'frequencies')
            durations_ms: Duration per phoneme in ms (from Dev 2 melodic output 'durations')

        Returns:
            float32 numpy array waveform at 22050 Hz
        """
        if not phonemes:
            return np.zeros(self.sample_rate, dtype=np.float32)
        if not f0_hz:
            raise ValueError("f0_hz list cannot be empty")
        if not durations_ms:
            raise ValueError("durations_ms list cannot be empty")

        logger.debug(
            f"Synthesizing {len(phonemes)} phonemes | "
            f"F0 range: {min(f0_hz):.1f}-{max(f0_hz):.1f} Hz | "
            f"Total duration: {sum(durations_ms):.0f}ms"
        )

        # Use HiFi-GAN if available, else fallback
        if self.model is not None:
            try:
                import torch
                phoneme_ids = torch.LongTensor(self._phonemes_to_ids(phonemes))
                f0_tensor = torch.FloatTensor(f0_hz)
                dur_tensor = torch.FloatTensor(durations_ms)

                with torch.no_grad():
                    waveform = self.model(
                        phoneme_ids.unsqueeze(0),
                        f0_tensor.unsqueeze(0),
                        dur_tensor.unsqueeze(0)
                    )
                return waveform.squeeze().cpu().numpy().astype(np.float32)

            except Exception as e:
                logger.warning(f"HiFi-GAN inference failed: {e}. Using fallback.")

        return self._rule_based_synthesis(phonemes, f0_hz, durations_ms)


if __name__ == "__main__":
    print("Testing SanskritVocoder with dummy input...")

    vocoder = SanskritVocoder()

    # Test with 'namasté' phonemes
    test_phonemes = ["n", "ə", "m", "ə", "s", "t", "eː"]
    test_f0 = [220.0, 220.0, 240.0, 240.0, 230.0, 230.0, 250.0]
    test_durations = [80, 100, 80, 100, 80, 80, 150]

    waveform = vocoder.synthesize(test_phonemes, test_f0, test_durations)

    import soundfile as sf
    sf.write("test_output.wav", waveform, vocoder.sample_rate)
    print(f"✅ Saved test_output.wav | shape: {waveform.shape} | sr: {vocoder.sample_rate}")
