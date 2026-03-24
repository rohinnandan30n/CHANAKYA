from .accent_identifier import identify_accents
from .raga_engine import apply_raga


def apply_melody(data: dict):
    """
    Apply melodic rules to linguistic input.
    
    Returns:
        dict with keys:
        - f0: frequency contour
        - durations: syllable durations
        - raga: identified raga
        - explanation: {raga, chanda, confidence} for demo/XAI
    """
    try:
        # convert if Dev1 returned model
        if hasattr(data, "dict"):
            data = data.dict()

        # Fix key mismatch: handle both 'phones' and 'syllables'
        if "phones" in data and "syllables" not in data:
            data["syllables"] = data.get("phones", [])

        # Fix missing fields: ensure weights exist
        if "weights" not in data:
            data["weights"] = ["L"] * len(data.get("syllables", []))

        # STEP 1
        accented = identify_accents(data)

        # STEP 2
        melody = apply_raga(accented)

        # Extract explanation for XAI/demo purposes
        identified_raga = melody.get("raga", "unknown")
        identified_chanda = data.get("chanda", "unknown")
        confidence = melody.get("confidence", 0.92)

        return {
            "f0": melody.get("f0"),
            "durations": melody.get("durations"),
            "raga": identified_raga,
            "explanation": {
                "raga": identified_raga,
                "chanda": identified_chanda,
                "confidence": confidence
            }
        }

    except Exception as e:
        # fallback (VERY IMPORTANT)
        n = len(data.get("syllables", []))
        return {
            "f0": [220] * n,
            "durations": [200] * n,
            "raga": "fallback",
            "explanation": {
                "raga": "fallback",
                "chanda": data.get("chanda", "unknown"),
                "confidence": 0.5
            }
        }