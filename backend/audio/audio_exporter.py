"""
audio_exporter.py - Dev 3: Neural Audio Engineer
Exports synthesized waveform to WAV/MP3.
Output path format agreed with Dev 4: output/{job_id}.wav
"""

import os
import logging
import numpy as np
from typing import Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SAMPLE_RATE = 22050
OUTPUT_DIR = "output"


def normalize_waveform(waveform: np.ndarray) -> np.ndarray:
    """Normalize waveform to [-1, 1] range."""
    max_val = np.max(np.abs(waveform))
    if max_val > 0:
        return waveform / max_val
    return waveform


def trim_silence(waveform: np.ndarray,
                 threshold: float = 0.01,
                 sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Trim leading and trailing silence."""
    frame_size = int(0.02 * sample_rate)  # 20ms frames
    energy = np.array([
        np.mean(np.abs(waveform[i:i+frame_size]))
        for i in range(0, len(waveform) - frame_size, frame_size)
    ])

    non_silent = np.where(energy > threshold)[0]
    if len(non_silent) == 0:
        return waveform

    start = non_silent[0] * frame_size
    end = (non_silent[-1] + 1) * frame_size
    trimmed = waveform[start:end]
    logger.debug(f"Trimmed silence: {len(waveform)} -> {len(trimmed)} samples")
    return trimmed


def export_wav(waveform: np.ndarray,
               job_id: str,
               sample_rate: int = SAMPLE_RATE,
               output_dir: str = OUTPUT_DIR) -> str:
    """
    Export waveform as WAV file.

    Args:
        waveform:    float32 numpy array from vocoder
        job_id:      job identifier from Dev 4's orchestrator
        sample_rate: sample rate (default 22050 Hz)
        output_dir:  output directory (default 'output/')

    Returns:
        Path to saved WAV file: output/{job_id}.wav
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{job_id}.wav")

    # Normalize + trim
    waveform = normalize_waveform(waveform)
    waveform = trim_silence(waveform, sample_rate=sample_rate)

    try:
        import soundfile as sf
        sf.write(output_path, waveform, sample_rate, subtype="PCM_16")
        logger.debug(f"WAV saved: {output_path}")
        return output_path

    except ImportError:
        # Fallback: write raw WAV without soundfile
        import wave
        import struct
        waveform_int = (waveform * 32767).astype(np.int16)
        with wave.open(output_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(struct.pack(f"{len(waveform_int)}h", *waveform_int))
        logger.debug(f"WAV saved (fallback): {output_path}")
        return output_path


def export_mp3(waveform: np.ndarray,
               job_id: str,
               sample_rate: int = SAMPLE_RATE,
               output_dir: str = OUTPUT_DIR,
               bitrate: str = "192k") -> Optional[str]:
    """
    Export waveform as MP3 file.

    Args:
        waveform:    float32 numpy array from vocoder
        job_id:      job identifier from Dev 4's orchestrator
        sample_rate: sample rate (default 22050 Hz)
        output_dir:  output directory
        bitrate:     MP3 bitrate (default 192k)

    Returns:
        Path to saved MP3 file or None if pydub unavailable
    """
    try:
        from pydub import AudioSegment

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{job_id}.mp3")

        waveform = normalize_waveform(waveform)
        waveform = trim_silence(waveform, sample_rate=sample_rate)

        waveform_int = (waveform * 32767).astype(np.int16)
        audio = AudioSegment(
            waveform_int.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1
        )
        audio.export(output_path, format="mp3", bitrate=bitrate)
        logger.debug(f"MP3 saved: {output_path}")
        return output_path

    except ImportError:
        logger.warning("pydub not installed, MP3 export unavailable")
        return None
    except Exception as e:
        logger.error(f"MP3 export failed: {e}")
        return None


if __name__ == "__main__":
    print("Testing audio_exporter with dummy waveform...")

    # Generate test tone
    duration = 1.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    test_waveform = (0.5 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)

    wav_path = export_wav(test_waveform, job_id="test_job_001")
    print(f"✅ WAV exported: {wav_path}")

    mp3_path = export_mp3(test_waveform, job_id="test_job_001")
    if mp3_path:
        print(f"✅ MP3 exported: {mp3_path}")
    else:
        print("⚠️  MP3 skipped (pydub not installed)")


def generate_audio(phonemes, f0_hz, durations_ms,
                   output_format="wav",
                   output_path="output/recitation.wav") -> dict:
    """
    Full audio generation: synthesize + export.
    Dev 4 / test contract entry point.
    """
    from backend.audio.vocoder import SanskritVocoder
    import os

    vocoder = SanskritVocoder()
    n = min(len(phonemes), len(f0_hz), len(durations_ms))
    waveform = vocoder.synthesize(phonemes[:n], f0_hz[:n], durations_ms[:n])

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    job_id = os.path.splitext(os.path.basename(output_path))[0]
    out_dir = os.path.dirname(output_path) or "output"

    if output_format == "mp3":
        path = export_mp3(waveform, job_id, output_dir=out_dir) or export_wav(waveform, job_id, output_dir=out_dir)
    else:
        path = export_wav(waveform, job_id, output_dir=out_dir)

    import soundfile as sf
    info = sf.info(path)
    return {
        "path": path,
        "duration_sec": round(info.duration, 3),
        "sample_rate": info.samplerate,
    }