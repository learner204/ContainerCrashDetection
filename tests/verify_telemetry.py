import time
from api_server import get_current_position

def test_telemetry_starts_at_origin():
    now = time.time()
    # Mock voyage data
    voyage = {
        "start_time": now,
        "waypoints": [
            {"lat": 10.0, "lng": 20.0, "name": "Start Port"},
            {"lat": 15.0, "lng": 25.0, "name": "Mid Point"},
            {"lat": 20.0, "lng": 30.0, "name": "End Port"}
        ],
        "is_active": True
    }
    
    # We need to mock time.time() to return 'now' exactly
    import api_server
    original_time = api_server.time.time
    api_server.time.time = lambda: now
    
    try:
        # Immediately at start, it should be exactly at the origin
        pos = get_current_position(voyage)
        print(f"Position at start: {pos}")
        
        assert pos["lat"] == 10.0
        assert pos["lng"] == 20.0
        assert pos["location_name"] == "Start Port"
        
        # After 1800s it should be at Mid Point.
        api_server.time.time = lambda: now + 1800
        pos_mid = get_current_position(voyage)
        print(f"Position at mid-way: {pos_mid}")
        
        # Jitter is enabled here, but since it's exactly on a waypoint, let's see
        # Actually, in my fix, jitter is 0.005 if progress is not near 0 or 1.
        # progress = 1800 / 3600 = 0.5.
        assert 14.99 < pos_mid["lat"] < 15.01
        assert 24.99 < pos_mid["lng"] < 25.01
        
        # At the very end (3600s)
        api_server.time.time = lambda: now + 3600
        pos_end = get_current_position(voyage)
        print(f"Position at end: {pos_end}")
        
        assert pos_end["lat"] == 20.0
        assert pos_end["lng"] == 30.0
    finally:
        api_server.time.time = original_time


if __name__ == "__main__":
    try:
        test_telemetry_starts_at_origin()
        print("Test passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
