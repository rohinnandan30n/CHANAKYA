import uuid

# Global in-memory job store
jobs = {}

def create_job():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "result": None}
    return job_id

def get_job(job_id):
    return jobs.get(job_id)

def update_job(job_id, status, result=None):
    if job_id in jobs:
        # If result is provided, update it; otherwise keep existing result if only status changes
        current_result = jobs[job_id].get("result")
        jobs[job_id] = {
            "status": status,
            "result": result if result is not None else current_result
        }
