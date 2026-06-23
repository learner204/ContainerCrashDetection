import math
from typing import List, Dict

class RouteService:
    """
    Handles coordinate interpolation and route geometry.
    Uses strategic transit hubs to avoid landmasses for major international routes.
    """

    # Strategic Maritime Choke Points & Waypoints
    HUBS = {
        "SUEZ_NORTH": {"lat": 31.26, "lng": 32.30, "name": "Port Said (Suez North)"},
        "SUEZ_SOUTH": {"lat": 29.97, "lng": 32.53, "name": "Suez Canal South"},
        "PANAMA_ATLANTIC": {"lat": 9.35, "lng": -79.92, "name": "Panama Canal (Atlantic)"},
        "PANAMA_PACIFIC": {"lat": 8.95, "lng": -79.56, "name": "Panama Canal (Pacific)"},
        "MALACCA_WEST": {"lat": 5.0, "lng": 95.0, "name": "Andaman Sea"},
        "MALACCA_EAST": {"lat": 1.3, "lng": 104.0, "name": "Singapore Strait"},
        "GIBRALTAR": {"lat": 36.0, "lng": -5.5, "name": "Strait of Gibraltar"},
        "BAB_EL_MANDEB": {"lat": 12.6, "lng": 43.3, "name": "Bab el-Mandeb"},
        "CAPE_GOOD_HOPE": {"lat": -34.4, "lng": 18.5, "name": "Cape of Good Hope"},
        "ENGLISH_CHANNEL": {"lat": 50.0, "lng": -3.0, "name": "English Channel"},
        "NORTH_SEA": {"lat": 54.0, "lng": 5.0, "name": "North Sea"},
        "US_EAST_OUTER": {"lat": 35.0, "lng": -70.0, "name": "US East Coast Outer"},
        "US_WEST_OUTER": {"lat": 35.0, "lng": -125.0, "name": "US West Coast Outer"}
    }

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Haversine formula to calculate distance in km."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_intermediate_points(self, start: Dict, end: Dict, num_points: int) -> List[Dict]:
        """Interpolates points on a single Great Circle segment."""
        lat1 = math.radians(start["lat"])
        lon1 = math.radians(start["lng"])
        lat2 = math.radians(end["lat"])
        lon2 = math.radians(end["lng"])

        # Handle crossing the International Date Line
        dlon = lon2 - lon1
        if dlon > math.pi:
            lon2 -= 2 * math.pi
        elif dlon < -math.pi:
            lon2 += 2 * math.pi
        
        # Avoid division by zero for identical points
        if lat1 == lat2 and lon1 == lon2:
            return [{"lat": start["lat"], "lng": start["lng"], "name": start.get("name", "Stationary")} for _ in range(num_points)]

        d = 2 * math.asin(math.sqrt(math.sin((lat1 - lat2) / 2)**2 +
                                    math.cos(lat1) * math.cos(lat2) * math.sin((lon1 - lon2) / 2)**2))

        segment_points = []
        for i in range(num_points):
            f = i / (num_points - 1)
            
            # Using slerp-like interpolation for Great Circle
            a = math.sin((1 - f) * d) / math.sin(d)
            b = math.sin(f * d) / math.sin(d)
            
            x = a * math.cos(lat1) * math.cos(lon1) + b * math.cos(lat2) * math.cos(lon2)
            y = a * math.cos(lat1) * math.sin(lon1) + b * math.cos(lat2) * math.sin(lon2)
            z = a * math.sin(lat1) + b * math.sin(lat2)
            
            res_lat = math.atan2(z, math.sqrt(x**2 + y**2))
            res_lon = math.atan2(y, x)
            
            # Normalize longitude back to -180 to 180
            deg_lon = math.degrees(res_lon)
            while deg_lon > 180: deg_lon -= 360
            while deg_lon < -180: deg_lon += 360
            
            segment_points.append({
                "lat": math.degrees(res_lat),
                "lng": deg_lon,
                "name": start.get("name", "In Transit")
            })
        return segment_points

    def get_route_waypoints(self, start: Dict, end: Dict, num_points: int = 100) -> List[Dict]:
        """
        Determines the best path using hubs and generates combined waypoints.
        """
        path = [start]
        
        s_lng = start["lng"]
        e_lng = end["lng"]
        s_lat = start["lat"]
        e_lat = end["lat"]

        def is_atlantic_side(lng):
            # Includes Europe, Africa, US East, South America East
            return -100 < lng < 45
        
        def is_pacific_side(lng):
            # Includes US West, Oceania, parts of Asia
            return -150 < lng < -100

        # 1. Asia/India <-> Europe/US East (via Suez)
        start_asia = (60 < s_lng <= 180) or (-180 <= s_lng < -160)
        end_asia = (60 < e_lng <= 180) or (-180 <= e_lng < -160)
        start_atl = is_atlantic_side(s_lng)
        end_atl = is_atlantic_side(e_lng)

        if (start_asia and end_atl) or (start_atl and end_asia):
            suez_hubs = [
                self.HUBS["MALACCA_EAST"],
                self.HUBS["MALACCA_WEST"],
                self.HUBS["BAB_EL_MANDEB"],
                self.HUBS["SUEZ_SOUTH"],
                self.HUBS["SUEZ_NORTH"]
            ]
            
            if (start_atl and s_lng < -5) or (end_atl and e_lng < -5):
                suez_hubs.append(self.HUBS["GIBRALTAR"])

            if start_asia: # Westbound
                filtered_hubs = [h for h in suez_hubs if h["lng"] < s_lng - 2]
                path.extend(filtered_hubs)
            else: # Eastbound
                suez_hubs.reverse()
                filtered_hubs = [h for h in suez_hubs if h["lng"] > s_lng + 2]
                path.extend(filtered_hubs)

        # 2. Atlantic <-> Pacific Americas (via Panama)
        elif (is_atlantic_side(s_lng) and is_pacific_side(e_lng)) or \
             (is_pacific_side(s_lng) and is_atlantic_side(e_lng)):
            
            panama_hubs = [self.HUBS["PANAMA_ATLANTIC"], self.HUBS["PANAMA_PACIFIC"]]
            if is_pacific_side(s_lng):
                panama_hubs.reverse()
            path.extend(panama_hubs)

        # 3. Intra-Asia (East Asia <-> South Asia/Middle East via Malacca)
        elif start_asia and end_asia:
            if (s_lng > 105 and e_lng < 95) or (s_lng < 95 and e_lng > 105):
                malacca_hubs = [self.HUBS["MALACCA_EAST"], self.HUBS["MALACCA_WEST"]]
                if s_lng < e_lng:
                    malacca_hubs.reverse()
                path.extend(malacca_hubs)

        # 4. Trans-Atlantic (US East <-> Europe)
        elif abs(s_lng - e_lng) > 40 and len(path) == 1:
            if s_lat > 40 or e_lat > 40:
                path.append(self.HUBS["NORTH_SEA"] if s_lng > 0 else self.HUBS["US_EAST_OUTER"])

        # 5. Coastal Europe (Mediterranean <-> North Sea/Atlantic)
        # Ensuring routes between the Mediterranean and Northern Europe go around the continent
        def is_med(lat, lng):
            return 30 < lat < 47 and -6 < lng < 40
        def is_north_europe(lat, lng):
            return lat >= 47 and -20 < lng < 40

        if (is_med(s_lat, s_lng) and is_north_europe(e_lat, e_lng)) or \
           (is_north_europe(s_lat, s_lng) and is_med(e_lat, e_lng)):
            # Avoid adding if already added via Suez logic
            if not any(h["name"] == "Strait of Gibraltar" for h in path):
                extra_hubs = [self.HUBS["GIBRALTAR"], self.HUBS["ENGLISH_CHANNEL"]]
                if is_north_europe(s_lat, s_lng):
                    extra_hubs.reverse()
                path.extend(extra_hubs)

        path.append(end)
        print(f"DEBUG: Route from {start.get('name')} to {end.get('name')} | Path Hubs: {[p.get('name') for p in path]}")
        
        # Generate final interpolated waypoints
        all_waypoints = []
        target_total = max(num_points, len(path) * 20)
        points_per_segment = target_total // (len(path) - 1)
        
        for i in range(len(path) - 1):
            segment = self.get_intermediate_points(path[i], path[i+1], points_per_segment)
            if i > 0:
                all_waypoints.extend(segment[1:])
            else:
                all_waypoints.extend(segment)
                
        return all_waypoints

route_service = RouteService()
