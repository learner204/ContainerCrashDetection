interface EventLog {
  id: number;
  timestamp: string;
  predicted_label: number;
  confidence: number;
  alert: string;
}

interface AnalysisResult {
  signal: number[];
  prediction: number;
  label: string;
  confidence: number;
  alert: string;
  timestamp: string;
}

export interface StreamData {
  is_active: boolean;
  signal: number[];
  prediction: number;
  label: string;
  confidence: number;
  alert: string;
  timestamp: string;
  telemetry: {
    lat: number;
    lng: number;
    location: string;
    vessel: string;
  };
  active_risk: number;
  route_name?: string;
}

const EVENT_LABELS: Record<number, string> = {
  0: "Normal",
  1: "Mild Impact",
  2: "Severe Crash",
  3: "Container Shift"
};

export interface VoyageAssessment {
  voyage_id: string;
  probability: number;
  risk_level: 'Low' | 'Medium' | 'High';
  waypoints: Array<{ lat: number; lng: number; name: string }>;
  weather_summary: {
    max_wave_height: number;
    max_wind_speed: number;
    duration_days: number;
    cargo_fragility: number;
  };
}

export type { EventLog, AnalysisResult };
export { EVENT_LABELS };
