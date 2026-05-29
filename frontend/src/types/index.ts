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
  3: "Unstable (Pre-Crash)"
};

export type { EventLog, AnalysisResult };
export { EVENT_LABELS };
