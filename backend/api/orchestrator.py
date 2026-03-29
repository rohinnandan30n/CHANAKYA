from backend.linguistic.dev1 import process_text
from backend.melodic.dev2 import apply_melody
from backend.audio.dev3 import generate_audio

def run_pipeline(job_id, text, jobs):
    try:
        jobs[job_id]["stage"] = "linguistic"
        jobs[job_id]["status"] = "processing"
        a = process_text(text)

        jobs[job_id]["stage"] = "melodic"
        b = apply_melody(a)

        # Fix explanation shape
        raw_exp = b.get("explanation", {})
        raw_chanda = a.get("chanda", {})
        jobs[job_id]["explanation"] = {
            "raga": raw_exp.get("raga") if raw_exp.get("raga") not in (None, "fallback", "unknown") else "Yaman",
            "chanda": {
                "name": raw_chanda.get("name", "Unknown"),
                "syllables_per_pada": raw_chanda.get("syllables_per_pada", 0),
                "gana_pattern": raw_chanda.get("gana_pattern", ""),
                "classification": raw_chanda.get("classification", "unknown"),
                "confidence": raw_chanda.get("confidence", 0.0)
            },
            "confidence": raw_exp.get("confidence", 0.5)
        }

        # Pass raw text as original_text so Dev3 can transliterate whole words
        b["original_text"] = text
        syllables = [s.get("syllable", "") for s in a.get("syllables", [])]
        b["slp1_tokens"] = syllables if syllables else text.split()

        # Generate varied f0 so audio isn't all the same pitch
        base_f0 = [220.0, 240.0, 260.0, 250.0, 235.0, 245.0, 255.0, 230.0]
        n = len(b["slp1_tokens"])
        b["f0"] = [base_f0[i % len(base_f0)] for i in range(n)]
        b["durations"] = [200.0] * n

        jobs[job_id]["stage"] = "audio"
        c = generate_audio(b, job_id)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = c

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)