import time
from backend.linguistic.dev1 import process_text
from backend.melodic.dev2 import apply_melody
from backend.audio.dev3 import generate_audio

def run_pipeline(job_id, text, jobs):
    try:
        # STEP 1 - Dev1 (linguistic)
        jobs[job_id]["stage"] = "linguistic"
        jobs[job_id]["status"] = "processing"
        a = process_text(text)

        # STEP 2 - Dev2 (melodic)
        jobs[job_id]["stage"] = "melodic"
        b = apply_melody(a)
        
        # Capture explanation for XAI/demo
        jobs[job_id]["explanation"] = b.get("explanation")

        # STEP 3 - Dev3 (audio)
        jobs[job_id]["stage"] = "audio"
        c = generate_audio(b, job_id)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = c

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
