"""Full integration test for Chanakya pipeline"""

import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_full_pipeline():
    print("=" * 60)
    print("CHANAKYA FULL INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Health check
    print("\n[1/4] Health check...")
    try:
        r = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✓ Health: {r.json()}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return
    
    # Step 2: POST /recite
    print("\n[2/4] POST /recite - Starting recitation job...")
    try:
        r = requests.post(f"{BASE_URL}/recite", params={"text": "namaste"}, timeout=10)
        recite_response = r.json()
        job_id = recite_response.get("job_id")
        print(f"✓ Recite started - Job ID: {job_id}")
        print(f"   Response: {recite_response}")
    except Exception as e:
        print(f"✗ Recite failed: {e}")
        return
    
    # Step 3: GET /status/{job_id} - Poll until completion
    print(f"\n[3/4] GET /status/{job_id} - Polling for completion...")
    max_wait = 30
    poll_interval = 1
    elapsed = 0
    
    while elapsed < max_wait:
        try:
            r = requests.get(f"{BASE_URL}/status/{job_id}", timeout=10)
            status_response = r.json()
            status = status_response.get("status")
            stage = status_response.get("stage")
            
            print(f"   [{elapsed}s] Status: {status}, Stage: {stage}")
            
            if status == "completed":
                print(f"✓ Job completed!")
                print(f"   Full response: {json.dumps(status_response, indent=2)}")
                break
            elif status == "failed":
                print(f"✗ Job failed: {status_response.get('error')}")
                return
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        except Exception as e:
            print(f"✗ Status check failed: {e}")
            return
    
    if elapsed >= max_wait:
        print(f"✗ Job did not complete within {max_wait} seconds")
        return
    
    # Step 4: GET /audio/{job_id}
    print(f"\n[4/4] GET /audio/{job_id} - Retrieving audio file...")
    try:
        r = requests.get(f"{BASE_URL}/audio/{job_id}", timeout=10)
        if r.status_code == 200:
            print(f"✓ Audio retrieved successfully")
            print(f"   Content-Type: {r.headers.get('content-type')}")
            print(f"   Content-Length: {len(r.content)} bytes")
            
            # Save to file for verification
            audio_file = f"test_output_{job_id}.wav"
            with open(audio_file, "wb") as f:
                f.write(r.content)
            print(f"   Saved to: {audio_file}")
        else:
            print(f"✗ Audio not ready: {r.json()}")
    except Exception as e:
        print(f"✗ Audio retrieval failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✓ FULL INTEGRATION TEST PASSED")
    print("=" * 60)

if __name__ == "__main__":
    test_full_pipeline()
