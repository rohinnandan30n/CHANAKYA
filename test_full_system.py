import requests
import time
import json

BASE_URL = "http://localhost:8001/api/v1"

print("=" * 60)
print("STEP 6: TEST FULL SYSTEM")
print("=" * 60)

# TEST 1: POST /recite
print("\n1️⃣ TEST: POST /recite")
print("-" * 60)
response = requests.post(f"{BASE_URL}/recite", params={"text": "namaste"})
print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {json.dumps(result, indent=2)}")
job_id = result.get("job_id")

if not job_id:
    print("❌ Failed to get job_id")
    exit(1)

# TEST 2: GET /status/{job_id}
print("\n2️⃣ TEST: GET /status/{job_id}")
print("-" * 60)
time.sleep(1)  # Give pipeline a second to start
response = requests.get(f"{BASE_URL}/status/{job_id}")
print(f"Status: {response.status_code}")
status = response.json()
print(f"Response: {json.dumps(status, indent=2)}")

# TEST 3: GET /audio/{job_id}
print("\n3️⃣ TEST: GET /audio/{job_id}")
print("-" * 60)
# Wait for job to complete
max_attempts = 30
for i in range(max_attempts):
    response = requests.get(f"{BASE_URL}/status/{job_id}")
    job_status = response.json()
    print(f"[{i+1}/{max_attempts}] Job status: {job_status.get('status')}")
    
    if job_status.get("status") == "completed":
        break
    time.sleep(1)

# Now get audio
response = requests.get(f"{BASE_URL}/audio/{job_id}")
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Content-Length: {len(response.content)} bytes")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED")
print("=" * 60)
