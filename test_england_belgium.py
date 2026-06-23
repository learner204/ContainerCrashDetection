from services.route_service import route_service

def test_route(name, start, end):
    print(f"Testing route: {name}")
    waypoints = route_service.get_route_waypoints(start, end)
    print(f"Number of waypoints: {len(waypoints)}")
    # Print first few and last few waypoints
    print("First 5 waypoints:")
    for wp in waypoints[:5]:
        print(wp)
    print("Last 5 waypoints:")
    for wp in waypoints[-5:]:
        print(wp)
    
    # Check if any waypoint has a longitude that suggests it's going the long way
    long_way = any(abs(wp["lng"] - start["lng"]) > 10 for wp in waypoints)
    print(f"Goes far away (long way)? {long_way}")
    print("-" * 20)

felixstowe = {"name": "Felixstowe (GBFXT), UK", "lat": 51.96, "lng": 1.34}
antwerp = {"name": "Antwerp (BEANR), Belgium", "lat": 51.27, "lng": 4.38}

test_route("Felixstowe to Antwerp", felixstowe, antwerp)
