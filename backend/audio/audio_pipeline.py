import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class AudioPipeline:
    def __init__(self, vocoder_checkpoint=None, device="cpu"):
        self.vocoder_checkpoint = vocoder_checkpoint or ""
        self.device = device
        self._sandhi_fn = None
        self._g2p = None
        self._exporter_fn = None

    def _get_sandhi(self):
        if self._sandhi_fn is None:
            from backend.audio.sandhi_processor import apply_sandhi, load_sandhi_rules
            try:
                rules = load_sandhi_rules()
            except Exception:
                rules = []
            self._sandhi_fn = lambda tokens: apply_sandhi(tokens, rules)
        return self._sandhi_fn

    def _get_g2p(self):
        if self._g2p is None:
            from backend.audio.g2p_converter import G2PConverter
            self._g2p = G2PConverter()
        return self._g2p

    def _get_exporter(self):
        if self._exporter_fn is None:
            from backend.audio.audio_exporter import generate_audio
            self._exporter_fn = generate_audio
        return self._exporter_fn

    def run(self, slp1_tokens, f0_hz, durations_ms,
            output_path="output/recitation.wav", output_format="wav"):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info("[Dev3] Stage 1/3: sandhi")
        sandhi_text = self._get_sandhi()(slp1_tokens)

        logger.info("[Dev3] Stage 2/3: G2P")
        phonemes = self._get_g2p().convert(sandhi_text)

        n = len(phonemes)
        f0_aligned  = (list(f0_hz)  + [220.0] * n)[:n]
        dur_aligned = (list(durations_ms) + [150.0] * n)[:n]

        logger.info("[Dev3] Stage 3/3: export")
        result = self._get_exporter()(
            phonemes=phonemes,
            f0_hz=f0_aligned,
            durations_ms=dur_aligned,
            output_format=output_format,
            output_path=output_path,
        )
        result["phonemes"] = phonemes
        return result

    def generate_demo(self, output_path="output/demo_namaste.wav"):
        return self.run(
            slp1_tokens=["namas", "te"],
            f0_hz=[220.0, 240.0, 260.0, 250.0, 230.0],
            durations_ms=[200.0, 180.0, 160.0, 180.0, 200.0],
            output_path=output_path,
        )


def _align_list(values, target_len, default):
    if len(values) >= target_len:
        return values[:target_len]
    return values + [default] * (target_len - len(values))


def run_audio_pipeline(data):
    """Main entry point for the audio pipeline.
    
    Args:
        data: Dictionary containing:
            - slp1_tokens: List of SLP1 tokens
            - f0_hz: List of fundamental frequencies in Hz
            - durations_ms: List of durations in milliseconds
            - output_path: (optional) Path to save output audio
            - output_format: (optional) Audio format (default: 'wav')
    
    Returns:
        Dictionary with synthesis results including generated audio path and phonemes.
    """
    pipeline = AudioPipeline()
    return pipeline.run(
        slp1_tokens=data.get("slp1_tokens", []),
        f0_hz=data.get("f0_hz", []),
        durations_ms=data.get("durations_ms", []),
        output_path=data.get("output_path", "output/recitation.wav"),
        output_format=data.get("output_format", "wav"),
    )


def generate_audio(data):
    """Convenience wrapper for audio generation.
    
    Args:
        data: Audio generation parameters (see run_audio_pipeline)
    
    Returns:
        Generated audio results
    """
    return run_audio_pipeline(data)


if __name__ == "__main__":
    # Demo execution
    demo_data = {
        "slp1_tokens": ["namas", "te"],
        "f0_hz": [220.0, 240.0, 260.0, 250.0, 230.0],
        "durations_ms": [200.0, 180.0, 160.0, 180.0, 200.0],
        "output_path": "output/demo_namaste.wav",
    }
    result = run_audio_pipeline(demo_data)
    print(f"Audio generated: {result}")