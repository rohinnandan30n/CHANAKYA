from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
import os
from backend.api.orchestrator import run_pipeline

router = APIRouter()

# Simple in-memory jobs store
jobs = {}

@router.post("/recite")
def recite(text: str, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "queued",
        "progress": 0,
        "result": None
    }
    background_tasks.add_task(run_pipeline, job_id, text, jobs)
    return {"job_id": job_id, "status": "queued"}

@router.get("/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"error": "job not found"})

@router.get("/audio/{job_id}")
def get_audio(job_id: str):
    job = jobs.get(job_id)

    if not job or job["status"] != "completed":
        return {"error": "not ready"}

    # In the orchestrator, 'result' is the output of generate_audio
    audio_path = job["result"]["file_path"]

    # Ensure directory exists for faked file response
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    if not os.path.exists(audio_path):
        with open(audio_path, "wb") as f:
            f.write(b"fake audio data")

    return FileResponse(audio_path)
