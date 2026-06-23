from services.route_service import route_service

def test_route(name, start, end):
    print(f"Testing route: {name}")
    waypoints = route_service.get_route_waypoints(start, end)
    # Check for land crossing by looking at waypoints
    # (Just printing hubs for now)
    hubs = [wp["name"] for wp in waypoints if wp["name"] != "In Transit" and wp["name"] not in [start["name"], end["name"]]]
    print(f"Hubs: {list(dict.fromkeys(hubs))}")
    print("-" * 20)

shanghai = {"lat": 31.23, "lng": 121.47, "name": "Shanghai"}
rotterdam = {"lat": 51.92, "lng": 4.47, "name": "Rotterdam"}
los_angeles = {"lat": 33.77, "lng": -118.19, "name": "Los Angeles"}
mumbai = {"lat": 18.94, "lng": 72.83, "name": "Mumbai"}

test_route("Shanghai to Rotterdam", shanghai, rotterdam)
test_route("Rotterdam to Los Angeles", rotterdam, los_angeles)
test_route("Shanghai to Mumbai", shanghai, mumbai)
test_route("Mumbai to Shanghai", mumbai, shanghai)
