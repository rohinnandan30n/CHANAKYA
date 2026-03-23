import time
from backend.mocks.mock_linguistic import process as process_text
from backend.mocks.mock_melodic import process as apply_melody
from backend.mocks.mock_audio import process as generate_audio

def run_pipeline(job_id, text, jobs):
    try:
        # STEP 1 - Dev1 (linguistic)
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10

        a = process_text(text)

        jobs[job_id]["progress"] = 33

        # STEP 2 - Dev2 (melodic)
        b = apply_melody(a)

        jobs[job_id]["progress"] = 66

        # STEP 3 - Dev3 (audio)
        c = generate_audio(b, job_id)

        jobs[job_id]["progress"] = 90

        # FINAL OUTPUT
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["result"] = c

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
