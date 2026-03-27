"""
Audio generation wrapper for dev3 - handles conversion and error fallback.
"""

from .audio_pipeline import run_audio_pipeline


def generate_audio(data: dict, job_id: str = None):
    """Generate audio from melodic input with error handling.
    
    Args:
        data: Dictionary from Dev2 (melodic) containing:
              - f0: List of fundamental frequencies in Hz
              - durations: List of durations in milliseconds
              - raga: Raga identifier
              - explanation: XAI data
        job_id: (optional) Job ID for tracking through pipeline
    
    Returns:
        Dictionary with audio_path and metadata for Dev4.
    """
    try:
        # convert if pydantic
        if hasattr(data, "dict"):
            data = data.dict()

        # Map Dev2 output keys to audio_pipeline expectations
        audio_data = {
            "slp1_tokens": [""],  # Placeholder - Dev2 doesn't provide raw tokens
            "f0_hz": data.get("f0", [220.0]),
            "durations_ms": data.get("durations", [200.0]),
            "output_path": f"output/{job_id}.wav" if job_id else "output/recitation.wav",
            "output_format": "wav"
        }

        result = run_audio_pipeline(audio_data)

        return {
            "audio_path": result.get("audio_path", "output.wav"),
            "file_path": result.get("audio_path", "output.wav"),
            "job_id": job_id,
            "raga": data.get("raga"),
            "explanation": data.get("explanation")
        }

    except Exception as e:
        print("Audio error:", e)

        # fallback (VERY IMPORTANT)
        fallback_path = f"output/fallback_{job_id}.wav" if job_id else "output/fallback.wav"
        return {
            "audio_path": fallback_path,
            "file_path": fallback_path,
            "job_id": job_id,
            "raga": data.get("raga", "unknown"),
            "error": str(e)
        }
