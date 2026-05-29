import requests
import asyncio
import websockets
import json
import time
import sys

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/stream"

def test_health():
    print("--- Testing Health Check ---")
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    print(f"Health: {resp.json()}")

def test_fleet():
    print("\n--- Testing Fleet API ---")
    resp = requests.get(f"{BASE_URL}/api/fleet")
    assert resp.status_code == 200
    fleet = resp.json()
    print(f"Fleet size: {len(fleet)}")
    assert len(fleet) > 0

def test_voyage_assessment():
    print("\n--- Testing Voyage Assessment ---")
    payload = {
        "origin": {"lat": 31.23, "lng": 121.47, "name": "Shanghai"},
        "destination": {"lat": 34.05, "lng": -118.24, "name": "Los Angeles"},
        "departure_date": "2026-06-01T00:00:00",
        "arrival_date": "2026-06-20T00:00:00",
        "cargo_fragility": 0.5,
        "container_count": 5000,
        "alignment_score": 0.9
    }
    resp = requests.post(f"{BASE_URL}/api/assess-voyage", json=payload)
    assert resp.status_code == 200
    assessment = resp.json()
    print(f"Assessment: Risk Level {assessment['risk_level']}, Prob {assessment['probability']:.2f}")

def test_signal_analysis():
    print("\n--- Testing Signal Analysis (ML) ---")
    for label_id in [0, 1, 2, 3]:
        resp = requests.post(f"{BASE_URL}/api/analyze/{label_id}")
        assert resp.status_code == 200
        data = resp.json()
        print(f"Label {label_id} -> Prediction: {data['label']} (Conf: {data['confidence']:.2f})")

def test_history():
    print("\n--- Testing History API ---")
    resp = requests.get(f"{BASE_URL}/api/history")
    assert resp.status_code == 200
    history = resp.json()
    print(f"History entries: {len(history)}")

def stress_test_api(n=50):
    print(f"\n--- Stress Testing Signal Analysis ({n} requests) ---")
    start_time = time.time()
    for i in range(n):
        label = i % 4
        requests.post(f"{BASE_URL}/api/analyze/{label}")
    end_time = time.time()
    print(f"Finished {n} requests in {end_time - start_time:.2f} seconds ({(n/(end_time - start_time)):.2f} req/s)")

async def drill_websocket():
    print("\n--- Testing WebSocket Streaming ---")
    # Start voyage first
    requests.post(f"{BASE_URL}/api/start-voyage")
    
    async with websockets.connect(WS_URL) as websocket:
        for i in range(5):
            message = await websocket.recv()
            data = json.loads(message)
            print(f"WS Recv {i}: {data['label']} at {data['telemetry']['location']} (Risk: {data['active_risk']:.2f})")
            assert "signal" in data
            assert "telemetry" in data

if __name__ == "__main__":
    time.sleep(2) # Wait for server to start
    try:
        test_health()
        test_fleet()
        test_voyage_assessment()
        test_signal_analysis()
        test_history()
        stress_test_api(50)
        asyncio.run(drill_websocket())
        print("\n✅ Mock Drill Completed Successfully!")
    except Exception as e:
        print(f"\n❌ Mock Drill Failed: {e}")
        sys.exit(1)
