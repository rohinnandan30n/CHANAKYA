import requests
import time
import json

BASE_URL = "http://localhost:8001/api/v1"

print("=" * 70)
print("STEP 8: DEMO PREP - Detailed Check")
print("=" * 70)

# Create a new job
print("\n1️⃣ Creating job with POST /recite")
response = requests.post(f"{BASE_URL}/recite", params={"text": "namaste"})
result = response.json()
job_id = result["job_id"]
print(f"✓ Job created: {job_id}\n")

# Keep polling until complete
print("2️⃣ Polling status...")
for i in range(1, 15):
    time.sleep(0.3)
    response = requests.get(f"{BASE_URL}/status/{job_id}")
    status_info = response.json()
    
    status = status_info.get("status", "N/A")
    stage = status_info.get("stage", "N/A")
    explanation = status_info.get("explanation")
    
    print(f"[{i}] Status: {status:12} | Stage: {stage:12} | Explanation: {explanation is not None}")
    
    if explanation:
        print(f"\n    ✓ EXPLANATION FOUND:")
        for key, val in explanation.items():
            print(f"      - {key}: {val}")
    
    if status == "completed":
        print(f"\n✓ Job completed at attempt {i}")
        break

print("\n" + "=" * 70)
print("Demo Features Summary")
print("=" * 70)
print(f"""
Endpoint: GET /status/{{job_id}}

Returns:
- status: Current job status (queued/processing/completed/failed)
- stage: Current pipeline stage (linguistic/melodic/audio)
- progress: Progress percentage
- explanation: {{raga, chanda, confidence}} for XAI
- result: Final audio file info

This enables:
✓ Real-time progress tracking in UI
✓ Transparent decision-making (XAI)
✓ User-friendly demo experience
""")
