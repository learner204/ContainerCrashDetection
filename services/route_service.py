import math
import heapq
from typing import List, Dict, Tuple

class RouteService:
    """
    Advanced routing service that uses a maritime node network to avoid landmasses.
    Implements Dijkstra's algorithm over a graph of maritime waypoints.
    """

    def __init__(self):
        # Maritime Nodes (lat, lng, name)
        self.NODES = {
            "SUEZ_N": {"lat": 31.26, "lng": 32.30, "name": "Suez Canal North"},
            "SUEZ_S": {"lat": 29.93, "lng": 32.56, "name": "Suez Canal South"},
            "PANAMA_E": {"lat": 9.35, "lng": -79.91, "name": "Panama Canal East"},
            "PANAMA_W": {"lat": 8.95, "lng": -79.56, "name": "Panama Canal West"},
            "GIBRALTAR": {"lat": 35.95, "lng": -5.31, "name": "Strait of Gibraltar"},
            "MALACCA_W": {"lat": 5.86, "lng": 95.34, "name": "Malacca Strait West"},
            "MALACCA_E": {"lat": 1.25, "lng": 103.85, "name": "Singapore / Malacca East"},
            "BAB_EL_MANDEB": {"lat": 12.58, "lng": 43.34, "name": "Bab el-Mandeb"},
            "CAPE_GOOD_HOPE": {"lat": -34.83, "lng": 19.99, "name": "Cape of Good Hope"},
            "CAPE_HORN": {"lat": -56.50, "lng": -67.27, "name": "Cape Horn"},
            "ADEN": {"lat": 12.00, "lng": 50.00, "name": "Gulf of Aden"},
            "ORMUZ": {"lat": 26.56, "lng": 56.45, "name": "Strait of Hormuz"},
            "ENGLISH_CHANNEL": {"lat": 50.00, "lng": -3.00, "name": "English Channel"},
            "CAPE_VERDE": {"lat": 15.00, "lng": -25.00, "name": "Cape Verde Transit"},
            "AZORES": {"lat": 38.00, "lng": -28.00, "name": "Azores Transit"},
            "PACIFIC_MID_N": {"lat": 30.00, "lng": -160.00, "name": "North Pacific Transit"},
            "PACIFIC_MID_S": {"lat": -20.00, "lng": -140.00, "name": "South Pacific Transit"},
            "INDIAN_MID": {"lat": -10.00, "lng": 80.00, "name": "Central Indian Ocean"},
            "TAIWAN_STRAIT": {"lat": 24.50, "lng": 119.50, "name": "Taiwan Strait"},
            "LOMBOK_STRAIT": {"lat": -8.50, "lng": 115.75, "name": "Lombok Strait"},
            "BASS_STRAIT": {"lat": -39.50, "lng": 145.00, "name": "Bass Strait"},
            "NORTH_SEA": {"lat": 55.00, "lng": 5.00, "name": "North Sea Transit"},
            "US_EAST_TRANSIT": {"lat": 35.00, "lng": -74.00, "name": "US East Coast Transit"},
            "US_WEST_TRANSIT": {"lat": 35.00, "lng": -122.00, "name": "US West Coast Transit"},
            "JAPAN_SOUTH": {"lat": 30.00, "lng": 135.00, "name": "South of Japan"},
            "PHILIPPINES_EAST": {"lat": 15.00, "lng": 125.00, "name": "East of Philippines"}
        }

        # Valid Edges (Avoid land by only connecting open sea nodes)
        self.EDGES = [
            ("SUEZ_N", "GIBRALTAR"), ("SUEZ_N", "NORTH_SEA"),
            ("SUEZ_S", "BAB_EL_MANDEB"),
            ("BAB_EL_MANDEB", "ADEN"),
            ("ADEN", "INDIAN_MID"), ("ADEN", "ORMUZ"),
            ("GIBRALTAR", "ENGLISH_CHANNEL"), ("GIBRALTAR", "AZORES"), ("GIBRALTAR", "CAPE_VERDE"),
            ("ENGLISH_CHANNEL", "NORTH_SEA"),
            ("AZORES", "US_EAST_TRANSIT"), ("AZORES", "CAPE_VERDE"),
            ("CAPE_VERDE", "CAPE_GOOD_HOPE"), ("CAPE_VERDE", "US_EAST_TRANSIT"),
            ("CAPE_GOOD_HOPE", "INDIAN_MID"),
            ("INDIAN_MID", "MALACCA_W"), ("INDIAN_MID", "LOMBOK_STRAIT"), ("INDIAN_MID", "BASS_STRAIT"),
            ("MALACCA_W", "MALACCA_E"),
            ("MALACCA_E", "TAIWAN_STRAIT"), ("MALACCA_E", "PHILIPPINES_EAST"), ("MALACCA_E", "LOMBOK_STRAIT"),
            ("TAIWAN_STRAIT", "JAPAN_SOUTH"),
            ("JAPAN_SOUTH", "PACIFIC_MID_N"), ("JAPAN_SOUTH", "PHILIPPINES_EAST"),
            ("PHILIPPINES_EAST", "PACIFIC_MID_N"), ("PHILIPPINES_EAST", "PACIFIC_MID_S"),
            ("PACIFIC_MID_N", "US_WEST_TRANSIT"), ("PACIFIC_MID_N", "PACIFIC_MID_S"),
            ("PACIFIC_MID_S", "US_WEST_TRANSIT"), ("PACIFIC_MID_S", "CAPE_HORN"),
            ("PANAMA_E", "US_EAST_TRANSIT"), ("PANAMA_E", "CAPE_VERDE"),
            ("PANAMA_W", "US_WEST_TRANSIT"), ("PANAMA_W", "PACIFIC_MID_N"), ("PANAMA_W", "PACIFIC_MID_S"),
            ("US_EAST_TRANSIT", "ENGLISH_CHANNEL"), ("US_EAST_TRANSIT", "CAPE_VERDE"),
            ("CAPE_HORN", "CAPE_GOOD_HOPE"), ("CAPE_HORN", "US_EAST_TRANSIT")
        ]

        self.graph = {}
        self._build_graph()

    def _build_graph(self):
        for node_id in self.NODES:
            self.graph[node_id] = []
        for start_id, end_id in self.EDGES:
            dist = self.calculate_distance(
                self.NODES[start_id]["lat"], self.NODES[start_id]["lng"],
                self.NODES[end_id]["lat"], self.NODES[end_id]["lng"]
            )
            self.graph[start_id].append((end_id, dist))
            self.graph[end_id].append((start_id, dist)) # Undirected graph

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Haversine formula to calculate distance in km."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        # Handle wrap around
        dlon = (dlon + math.pi) % (2 * math.pi) - math.pi
        
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _dijkstra(self, start_node_id, end_node_id):
        distances = {node_id: float('infinity') for node_id in self.NODES}
        distances[start_node_id] = 0
        pq = [(0, start_node_id)]
        previous_nodes = {node_id: None for node_id in self.NODES}

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node == end_node_id:
                path = []
                while current_node:
                    path.append(current_node)
                    current_node = previous_nodes[current_node]
                return path[::-1]

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.graph[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        return []

    def get_route_waypoints(self, start: Dict, end: Dict, num_points: int = 100) -> List[Dict]:
        """
        Calculates a land-avoiding route using the maritime network.
        """
        # 1. Find nearest maritime nodes for start and end
        start_nearest = None
        min_start_dist = float('inf')
        end_nearest = None
        min_end_dist = float('inf')

        for node_id, node_data in self.NODES.items():
            ds = self.calculate_distance(start["lat"], start["lng"], node_data["lat"], node_data["lng"])
            if ds < min_start_dist:
                min_start_dist = ds
                start_nearest = node_id
            
            de = self.calculate_distance(end["lat"], end["lng"], node_data["lat"], node_data["lng"])
            if de < min_end_dist:
                min_end_dist = de
                end_nearest = node_id

        # 2. Find path between maritime nodes
        node_path = self._dijkstra(start_nearest, end_nearest)
        
        # 3. Build full path of coordinates
        full_path_coords = [start]
        for node_id in node_path:
            full_path_coords.append(self.NODES[node_id])
        full_path_coords.append(end)

        # 4. Interpolate points between waypoints
        all_waypoints = []
        points_per_segment = max(2, num_points // (len(full_path_coords) - 1))
        
        for i in range(len(full_path_coords) - 1):
            segment = self.get_intermediate_points(full_path_coords[i], full_path_coords[i+1], points_per_segment)
            if i > 0:
                all_waypoints.extend(segment[1:])
            else:
                all_waypoints.extend(segment)
                
        return all_waypoints

    def get_intermediate_points(self, start: Dict, end: Dict, num_points: int) -> List[Dict]:
        """Interpolates points on a single Great Circle segment."""
        lat1 = math.radians(start["lat"])
        lon1 = math.radians(start["lng"])
        lat2 = math.radians(end["lat"])
        lon2 = math.radians(end["lng"])

        dlon = lon2 - lon1
        # Normalize dlon to -pi to pi
        dlon = (dlon + math.pi) % (2 * math.pi) - math.pi
        lon2 = lon1 + dlon
        
        d = 2 * math.asin(math.sqrt(math.sin((lat1 - lat2) / 2)**2 +
                                    math.cos(lat1) * math.cos(lat2) * math.sin((lon1 - lon2) / 2)**2))

        segment_points = []
        for i in range(num_points):
            f = i / (num_points - 1)
            if d == 0:
                segment_points.append({"lat": start["lat"], "lng": start["lng"]})
                continue

            a = math.sin((1 - f) * d) / math.sin(d)
            b = math.sin(f * d) / math.sin(d)
            
            x = a * math.cos(lat1) * math.cos(lon1) + b * math.cos(lat2) * math.cos(lon2)
            y = a * math.cos(lat1) * math.sin(lon1) + b * math.cos(lat2) * math.sin(lon2)
            z = a * math.sin(lat1) + b * math.sin(lat2)
            
            res_lat = math.atan2(z, math.sqrt(x**2 + y**2))
            res_lon = math.atan2(y, x)
            
            deg_lon = math.degrees(res_lon)
            if deg_lon > 180: deg_lon -= 360
            if deg_lon < -180: deg_lon += 360
            
            segment_points.append({
                "lat": math.degrees(res_lat),
                "lng": deg_lon,
                "name": start.get("name", "In Transit")
            })
        return segment_points

route_service = RouteService()
