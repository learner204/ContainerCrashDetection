import joblib
import numpy as np
import warnings
from datetime import datetime
from sensors.feature_engineering import extract_features
from database.db import DatabaseManager

class CrashDetector:
    def __init__(self, model_path="models/crash_model.pkl"):
        # Note: Model was trained with scikit-learn 1.7.2 but environment uses 1.6.1.
        # Suppress the UserWarning warning from version mismatch.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            self.model = joblib.load(model_path)
        self.db_manager = DatabaseManager()

    def log_event(self, pred, conf, alert):
        """
        Log event to database with proper type conversion using connection pool.
        """
        # Ensure proper type conversion
        predicted_label = int(pred) if pred is not None else None
        confidence = float(conf) if conf is not None else None
        
        # Validate that we have valid values
        if predicted_label is None:
            raise ValueError(f"Invalid prediction value: {pred}")
        if confidence is None:
            raise ValueError(f"Invalid confidence value: {conf}")
        
        with self.db_manager.get_connection() as conn:
            conn.execute(
                "INSERT INTO events (timestamp, predicted_label, confidence, alert) VALUES (?, ?, ?, ?)",
                (datetime.now().isoformat(), predicted_label, confidence, str(alert))
            )
            conn.commit()

    def predict(self, signal):
        """
        Predict event type using extracted features and raw model probabilities.
        Returns the prediction and the raw model confidence.
        """
        features = extract_features(signal)
        
        # Get raw probabilities from the model
        proba = self.model.predict_proba([features])[0]
        pred = int(np.argmax(proba))
        confidence = float(np.max(proba))
        
        # Log feature-based insights (for debugging/transparency)
        # signal_max = np.max(np.abs(signal))
        # if signal_max > 15: # Extreme physical event
        #    ...
            
        return pred, confidence

# For backward compatibility
_default_detector = None

def get_detector():
    global _default_detector
    if _default_detector is None:
        _default_detector = CrashDetector()
    return _default_detector

def predict(signal):
    return get_detector().predict(signal)

def log_event(pred, conf, alert):
    get_detector().log_event(pred, conf, alert)
