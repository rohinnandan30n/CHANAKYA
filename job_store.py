import uuid
jobs = {}

def create_job():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "result": None}
    return job_id

def get_job(job_id):
    return jobs.get(job_id)

def update_job(job_id, status, result=None):
    if job_id in jobs:
        jobs[job_id] = {"status": status, "result": result}
