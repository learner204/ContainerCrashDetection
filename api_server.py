from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
import random
import joblib
import numpy as np
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Any

from sensors.signal_generator import SignalGenerator
from services.detector import CrashDetector
from services.alert_engine import AlertManager
from database.db import DatabaseManager
from config.settings import EVENT_LABELS
from config.routes import SHANGHAI_LA_ROUTE, VESSEL_CONFIG
from services.weather_service import weather_service
from services.route_service import route_service

app = FastAPI(title="Container Crash Detection API")

@app.on_event("startup")
async def startup_event():
    db_manager.init_db()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
detector = CrashDetector()
alert_manager = AlertManager()
signal_generator = SignalGenerator()

# Load Risk Model
try:
    risk_model = joblib.load("models/risk_model.pkl")
except Exception as e:
    print(f"Warning: Could not load risk model: {e}")
    risk_model = None

# Active Voyage State (The Bridge)
active_voyage = {
    "wave_height": 1.5,
    "wind_speed": 15.0,
    "alignment_score": 1.0,
    "probability": 0.05,
    "waypoints": SHANGHAI_LA_ROUTE,
    "route_name": "Shanghai to Los Angeles",
    "is_active": False,
    "start_time": 0
}

# Fleet Simulation State
FLEET_NAMES = ["MV Arctic Explorer", "MV Pacific Horizon", "MV Atlantic Shield", "MV Indian Star", "MV Southern Cross", "MV Northern Light", "MV Global Carrier", "MV Ocean Titan", "MV Emerald Wave", "MV Sapphire Sky"]
fleet_vessels = []

def initialize_fleet():
    global fleet_vessels
    for name in FLEET_NAMES:
        # Pick two random ports for a route
        from config.routes import SHANGHAI_LA_ROUTE # Use as template
        vessel = {
            "id": name.lower().replace(" ", "_"),
            "name": name,
            "vessel_type": "Post-Panamax Container",
            "lat": random.uniform(-40, 60),
            "lng": random.uniform(-170, 170),
            "status": random.choice(["Normal", "Warning", "Normal", "Normal"]), # Weighted to Normal
            "risk_score": random.uniform(0.05, 0.4),
            "cargo_value": random.uniform(10, 80), # Millions USD
            "teu_count": random.randint(5000, 15000),
            "destination": "Random Port",
            "speed": random.uniform(18.0, 24.0)
        }
        fleet_vessels.append(vessel)

initialize_fleet()

def update_fleet_positions():
    global fleet_vessels
    for v in fleet_vessels:
        # Move them slightly
        v["lat"] += random.uniform(-0.01, 0.01)
        v["lng"] += random.uniform(-0.01, 0.01)
        # Randomly jitter risk
        v["risk_score"] = max(0.05, min(0.95, v["risk_score"] + random.uniform(-0.02, 0.02)))
        if v["risk_score"] > 0.7: v["status"] = "Critical"
        elif v["risk_score"] > 0.4: v["status"] = "Warning"
        else: v["status"] = "Normal"

@app.get("/api/fleet")
async def get_fleet():
    update_fleet_positions()
    return fleet_vessels

class Location(BaseModel):
    lat: float
    lng: float
    name: str

class VoyageRequest(BaseModel):
    origin: Location
    destination: Location
    departure_date: str
    arrival_date: str
    cargo_fragility: float
    container_count: int
    alignment_score: float

@app.get("/api/history")
async def get_history():
    try:
        conn = db_manager.get_connection()
        conn.row_factory = lambda cursor, row: {
            col[0]: row[idx] for idx, col in enumerate(cursor.description)
        }
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 100")
        history = cursor.fetchall()
        conn.close()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assess-voyage")
async def assess_voyage(request: VoyageRequest):
    try:
        # Increase points for a smoother Great Circle curve
        waypoints = route_service.get_route_waypoints(request.origin.dict(), request.destination.dict(), num_points=50)
        midpoint = waypoints[len(waypoints)//2]
        weather = weather_service.fetch_marine_weather(midpoint["lat"], midpoint["lng"])
        
        d1 = datetime.fromisoformat(request.departure_date)
        d2 = datetime.fromisoformat(request.arrival_date)
        duration_days = max(1, (d2 - d1).days)
        
        prob = 0.05
        if risk_model:
            features = np.array([[
                weather["max_wave_height"],
                weather["max_wind_speed"],
                duration_days,
                request.cargo_fragility,
                request.container_count,
                request.alignment_score
            ]])
            prob = risk_model.predict(features)[0]
        
        risk_level = "Low"
        if prob > 0.6: risk_level = "High"
        elif prob > 0.3: risk_level = "Medium"
        
        # Update Active Voyage State for the Bridge
        global active_voyage
        
        # Add names to waypoints for telemetry
        named_waypoints = []
        for i, wp in enumerate(waypoints):
            name = "In Transit"
            if i == 0: name = request.origin.name
            elif i == len(waypoints) - 1: name = request.destination.name
            named_waypoints.append({**wp, "name": name})

        active_voyage = {
            "wave_height": weather["max_wave_height"],
            "wind_speed": weather["max_wind_speed"],
            "alignment_score": request.alignment_score,
            "probability": float(prob),
            "waypoints": named_waypoints,
            "route_name": f"{request.origin.name} to {request.destination.name}",
            "is_active": False # Reset activity until explicitly started
        }
        
        return {
            "probability": float(prob),
            "risk_level": risk_level,
            "waypoints": waypoints,
            "route_name": active_voyage["route_name"],
            "weather_summary": {
                **weather,
                "duration_days": duration_days,
                "cargo_fragility": request.cargo_fragility
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_current_position():
    import time
    if not active_voyage["is_active"] or active_voyage["start_time"] == 0:
        route = active_voyage.get("waypoints", SHANGHAI_LA_ROUTE)
        return {
            "lat": route[0]["lat"],
            "lng": route[0]["lng"],
            "location_name": route[0].get("name", "Origin")
        }

    # Voyage lasts 10 minutes (600 seconds) for demo purposes
    voyage_duration = 600 
    elapsed = time.time() - active_voyage["start_time"]
    progress = min(1.0, elapsed / voyage_duration)
    
    route = active_voyage.get("waypoints", SHANGHAI_LA_ROUTE)
    num_points = len(route)
    
    idx = int(progress * (num_points - 1))
    next_idx = min(idx + 1, num_points - 1)
    segment_progress = (progress * (num_points - 1)) - idx if num_points > 1 else 0
    
    p1 = route[idx]
    p2 = route[next_idx]
    
    base_lat = p1["lat"] + (p2["lat"] - p1["lat"]) * segment_progress
    base_lng = p1["lng"] + (p2["lng"] - p1["lng"]) * segment_progress
    
    # Handle longitude wrap-around for international date line
    if abs(p2["lng"] - p1["lng"]) > 180:
        if p2["lng"] > p1["lng"]:
            base_lng = p1["lng"] + (p2["lng"] - 360 - p1["lng"]) * segment_progress
        else:
            base_lng = p1["lng"] + (p2["lng"] + 360 - p1["lng"]) * segment_progress
        if base_lng > 180: base_lng -= 360
        if base_lng < -180: base_lng += 360

    jitter = 0.005
    return {
        "lat": base_lat + random.uniform(-jitter, jitter),
        "lng": base_lng + random.uniform(-jitter, jitter),
        "location_name": p1.get("name", "In Transit")
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "endpoints": ["/api/history", "/api/assess-voyage", "/api/start-voyage", "/api/analyze/{label_id}", "/ws/stream"]}

@app.post("/api/analyze/{label_id}")
async def analyze_signal(label_id: int):
    try:
        signal = signal_generator.generate_signal(label_id)
        pred, conf = detector.predict(signal)
        alert = alert_manager.get_alert(pred, conf)
        
        return {
            "signal": signal[-250:].tolist(),
            "prediction": int(pred),
            "label": EVENT_LABELS[pred],
            "confidence": float(conf),
            "alert": alert,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/start-voyage")
async def start_voyage():
    global active_voyage
    active_voyage["is_active"] = True
    import time
    active_voyage["start_time"] = time.time()
    return {"status": "Voyage started"}

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if not active_voyage["is_active"]:
                await websocket.send_text(json.dumps({
                    "is_active": False,
                    "route_name": active_voyage.get("route_name", "None")
                }))
                await asyncio.sleep(1)
                continue

            # Operational Bridge: Assessment parameters drive real-time simulation
            label = 0
            # Higher predicted probability = higher frequency of actual crash events
            event_threshold = active_voyage["probability"] * 0.15 
            r = random.random()
            if r < event_threshold:
                label = random.choice([1, 2])
            elif r < event_threshold * 2.5: # 2.5x more likely to see a warning before a crash
                label = 3 # Pre-Crash Warning
                
            signal = signal_generator.generate_signal(
                label, 
                wave_height=active_voyage["wave_height"],
                wind_speed=active_voyage["wind_speed"],
                alignment_score=active_voyage["alignment_score"]
            )
            # Override detector for simulation demo if label is 3
            if label == 3:
                pred, conf = 3, 0.85
            else:
                pred, conf = detector.predict(signal)
            alert = alert_manager.get_alert(pred, conf)
            
            # Operational Bridge: Log critical events to database
            if pred != 0:
                detector.log_event(pred, conf, alert)
                
            pos = get_current_position()
            
            await websocket.send_text(json.dumps({
                "is_active": True,
                "signal": signal[-50:].tolist(),
                "prediction": int(pred),
                "label": EVENT_LABELS[pred],
                "confidence": float(conf),
                "alert": alert,
                "timestamp": datetime.now().isoformat(),
                "telemetry": {
                    "lat": pos["lat"],
                    "lng": pos["lng"],
                    "location": pos["location_name"],
                    "vessel": VESSEL_CONFIG["name"]
                },
                "active_risk": active_voyage["probability"],
                "route_name": active_voyage.get("route_name", "Unknown Route")
            }))
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
