"""
Audio generation wrapper for dev3 - gTTS with Devanagari conversion.
"""
import os
from gtts import gTTS


# Manual fixes for SLP1 tokens that don't transliterate well
SLP1_FIXES = {
    "OM": "ॐ",
    "om": "ॐ",
    "AUM": "ॐ",
    "aum": "ॐ",
    "namaH": "नमः",
    "svaH": "स्वः",
    "BUH": "भूः",
    "BuvaH": "भुवः",
}


def _slp1_to_devanagari(slp1_text: str) -> str:
    """Convert SLP1 encoded text to Devanagari for proper TTS pronunciation."""
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate

    words = slp1_text.split()
    result = []
    for word in words:
        if word in SLP1_FIXES:
            result.append(SLP1_FIXES[word])
        else:
            try:
                result.append(transliterate(word, sanscript.SLP1, sanscript.DEVANAGARI))
            except Exception:
                result.append(word)
    return " ".join(result)


def generate_audio(data: dict, job_id: str = None):
    try:
        if hasattr(data, "dict"):
            data = data.dict()

        tokens = data.get("slp1_tokens", [])
        original_text = data.get("original_text", "")

        # Join syllables back into words using original_text as source of truth
        slp1_text = original_text if original_text else " ".join(tokens) if tokens else "om"
        slp1_text = slp1_text.replace("A UM", "OM").replace("a um", "om")
        devanagari = _slp1_to_devanagari(slp1_text)
        devanagari = devanagari.replace("ओम्", "ॐ").replace("ओम", "ॐ")


        print(f"[Dev3] original_text: {original_text}")
        print(f"[Dev3] tokens:        {tokens}")
        print(f"[Dev3] SLP1:          {slp1_text}")
        print(f"[Dev3] Devanagari: {devanagari}")

        mp3_path = f"output/{job_id}.mp3" if job_id else "output/recitation.mp3"
        os.makedirs("output", exist_ok=True)

        tts = gTTS(devanagari, lang='hi', slow=True)
        tts.save(mp3_path)

        return {
            "audio_path": mp3_path,
            "file_path": mp3_path,
            "job_id": job_id,
            "raga": data.get("raga", "Yaman"),
        }

    except Exception as e:
        print(f"[Dev3] Audio error: {e}")
        import wave, struct, math
        fallback_path = f"output/fallback_{job_id}.wav" if job_id else "output/fallback.wav"
        os.makedirs("output", exist_ok=True)
        sample_rate = 22050
        samples = []
        base_f0 = [220.0, 240.0, 260.0, 250.0, 235.0, 245.0]
        tokens_list = data.get("slp1_tokens", ["om"])
        for i in range(len(tokens_list)):
            freq = base_f0[i % len(base_f0)]
            for j in range(int(sample_rate * 0.2)):
                t = j / sample_rate
                val = 0.4 * math.sin(2 * math.pi * freq * t)
                samples.append(int(val * 32767))
        with wave.open(fallback_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(struct.pack(f'{len(samples)}h', *samples))
        return {
            "audio_path": fallback_path,
            "file_path": fallback_path,
            "job_id": job_id,
            "raga": data.get("raga", "Yaman"),
            "error": str(e)
        }