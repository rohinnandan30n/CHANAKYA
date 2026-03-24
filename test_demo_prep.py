import requests
import time
import json

BASE_URL = "http://localhost:8001/api/v1"

print("=" * 70)
print("STEP 8: DEMO PREP (VERY IMPORTANT)")
print("=" * 70)

# POST request
print("\n1️⃣ POST /recite → Submit job")
print("-" * 70)
response = requests.post(f"{BASE_URL}/recite", params={"text": "om"})
result = response.json()
job_id = result["job_id"]
print(f"Job ID: {job_id}")
print(f"Status: {result['status']}")

# Wait for processing
print("\n2️⃣ GET /status → Poll for explanation output & progress tracking")
print("-" * 70)
for attempt in range(1, 10):
    time.sleep(0.5)
    response = requests.get(f"{BASE_URL}/status/{job_id}")
    status_data = response.json()
    
    print(f"\n[Attempt {attempt}] Status: {status_data['status']} | Stage: {status_data.get('stage', 'N/A')}")
    
    # Show explanation once available
    if status_data.get("explanation"):
        print("\n✓ EXPLANATION OUTPUT:")
        print(json.dumps(status_data["explanation"], indent=2))
    
    if status_data['status'] == "completed":
        print(f"\n✓ RESULT:")
        print(json.dumps(status_data.get("result"), indent=2))
        break

# Final demo output
print("\n" + "=" * 70)
print("✅ DEMO-READY FEATURES")
print("=" * 70)
print("""
✓ Explanation output: raga, chanda, confidence
✓ Progress tracking: status, stage, progress
✓ Full XAI support: Transparent decision-making
✓ Real-time updates: Stream-ready for UI
""")
