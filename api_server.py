from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
import random
import joblib
import numpy as np
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any

from sensors.signal_generator import SignalGenerator
from services.detector import CrashDetector
from services.alert_engine import AlertManager
from database.db import DatabaseManager
from config.settings import EVENT_LABELS
from config.routes import SHANGHAI_LA_ROUTE, VESSEL_CONFIG
from services.weather_service import weather_service
from services.route_service import route_service
from services.voyage_manager import voyage_manager

app = FastAPI(title="Container Crash Detection API")

# Security: Tighten CORS for production readiness
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    name: str = Field(..., min_length=1)

class VoyageRequest(BaseModel):
    origin: Location
    destination: Location
    departure_date: str
    arrival_date: str
    cargo_fragility: float = Field(0.5, ge=0.1, le=1.0)
    container_count: int = Field(500, ge=1, le=25000)
    alignment_score: float = Field(0.9, ge=0.5, le=1.0)

    @field_validator('arrival_date')
    @classmethod
    def arrival_must_be_after_departure(cls, v, info):
        if 'departure_date' in info.data:
            try:
                d1 = datetime.fromisoformat(info.data['departure_date']).date()
                d2 = datetime.fromisoformat(v).date()
                if d2 < d1:
                    raise ValueError('Arrival date cannot be before departure date')
            except ValueError as e:
                if 'Arrival date' in str(e): raise
        return v

@app.get("/api/history")
async def get_history():
    try:
        with db_manager.get_connection() as conn:
            conn.row_factory = lambda cursor, row: {
                col[0]: row[idx] for idx, col in enumerate(cursor.description)
            }
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT 100")
            history = cursor.fetchall()
            return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assess-voyage")
async def assess_voyage(request: VoyageRequest):
    if request.origin.lat == request.destination.lat and request.origin.lng == request.destination.lng:
        raise HTTPException(status_code=400, detail="Origin and destination cannot be the same location")
    try:
        # Increase points for a smoother Great Circle curve and better land avoidance
        waypoints = route_service.get_route_waypoints(request.origin.dict(), request.destination.dict(), num_points=200)
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
        
        # Add names to waypoints for telemetry
        named_waypoints = []
        for i, wp in enumerate(waypoints):
            name = "In Transit"
            if i == 0: name = request.origin.name
            elif i == len(waypoints) - 1: name = request.destination.name
            named_waypoints.append({**wp, "name": name})

        # Create a new voyage session
        voyage_id = voyage_manager.create_voyage({
            "wave_height": weather["max_wave_height"],
            "wind_speed": weather["max_wind_speed"],
            "alignment_score": request.alignment_score,
            "probability": float(prob),
            "waypoints": named_waypoints,
            "route_name": f"{request.origin.name} to {request.destination.name}",
        })
        
        return {
            "voyage_id": voyage_id,
            "probability": float(prob),
            "risk_level": risk_level,
            "waypoints": waypoints,
            "weather_summary": {
                **weather,
                "duration_days": duration_days,
                "cargo_fragility": request.cargo_fragility
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_current_position(voyage: Dict[str, Any] = None):
    import time
    # Cycle duration in seconds (3600s = 1 hour for a full trip)
    cycle_duration = 3600 
    
    start_time = voyage.get("start_time") if voyage else None
    if start_time:
        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / cycle_duration)
    else:
        # Fallback to absolute time if start_time is missing
        progress = (time.time() % cycle_duration) / cycle_duration
    
    route = voyage.get("waypoints", SHANGHAI_LA_ROUTE) if voyage else SHANGHAI_LA_ROUTE
    num_points = len(route)
    
    if num_points < 2:
        return {"lat": 0, "lng": 0, "location_name": "Unknown"}

    idx = int(progress * (num_points - 1))
    if idx >= num_points - 1:
        idx = num_points - 2
        segment_progress = 1.0
    else:
        segment_progress = (progress * (num_points - 1)) - idx
    
    p1 = route[idx]
    p2 = route[idx + 1]
    
    # Handle longitude wrap-around for international date line
    lon1 = p1["lng"]
    lon2 = p2["lng"]
    
    if abs(lon2 - lon1) > 180:
        if lon2 > lon1:
            lon2 -= 360
        else:
            lon2 += 360
            
    base_lat = p1["lat"] + (p2["lat"] - p1["lat"]) * segment_progress
    base_lng = lon1 + (lon2 - lon1) * segment_progress
    
    # Final normalization
    if base_lng > 180: base_lng -= 360
    if base_lng < -180: base_lng += 360

    # Eliminate jitter at the exact start and end for precision
    jitter = 0.003 # Reduced jitter for more stability
    if progress < 0.001 or progress > 0.999:
        jitter = 0
        
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
    if label_id not in (0, 1, 2, 3):
        raise HTTPException(status_code=400, detail=f"Invalid label_id: {label_id}. Must be 0, 1, 2, or 3.")
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
async def start_voyage(voyage_id: str):
    success = voyage_manager.start_voyage(voyage_id)
    if not success:
        raise HTTPException(status_code=404, detail="Voyage session not found")
    return {"status": "Voyage started", "voyage_id": voyage_id}

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket, voyage_id: str = None):
    await websocket.accept()
    # State for realistic event triggering
    cumulative_stress = 0.0 
    
    try:
        while True:
            voyage = voyage_manager.get_voyage(voyage_id) if voyage_id else None
            
            if not voyage or not voyage.get("is_active"):
                await websocket.send_text(json.dumps({
                    "is_active": False,
                    "route_name": voyage.get("route_name", "None") if voyage else "No active voyage"
                }))
                await asyncio.sleep(1)
                continue

            # --- ML Realism: Physics-based Event Triggering ---
            label = 0
            
            # Base stress from weather (waves + wind)
            # Alignment score acts as a dampener (1.0 = perfect, 0.5 = loose)
            weather_stress = (voyage["wave_height"] * 0.2) + (voyage["wind_speed"] * 0.05)
            alignment_penalty = 1.2 - voyage["alignment_score"]
            
            current_stress = weather_stress * alignment_penalty
            cumulative_stress += (current_stress * 0.01) # Slow build up
            
            # Chance of event increases with stress
            event_threshold = (voyage["probability"] * 0.1) + (cumulative_stress * 0.05)
            
            if random.random() < event_threshold:
                # Decide event type based on severity of current stress
                if current_stress > 4.0 or random.random() < 0.2:
                    label = 2 # Severe Crash
                elif current_stress > 2.0:
                    label = 1 # Mild Impact
                else:
                    label = 3 # Container Shift
                
                cumulative_stress = 0 # Reset after event
            # --------------------------------------------------
                
            signal = signal_generator.generate_signal(
                label, 
                wave_height=voyage["wave_height"],
                wind_speed=voyage["wind_speed"],
                alignment_score=voyage["alignment_score"]
            )
            pred, conf = detector.predict(signal)
            alert = alert_manager.get_alert(pred, conf)
            
            # Operational Bridge: Log critical events to database
            if pred != 0:
                detector.log_event(pred, conf, alert)
                
            pos = get_current_position(voyage)
            
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
                "active_risk": voyage["probability"],
                "route_name": voyage.get("route_name", "Unknown Route")
            }))
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
