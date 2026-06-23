from config.settings import SEVERITY_THRESHOLDS, SEVERITY_LEVELS

class AlertManager:
    def __init__(self, thresholds=SEVERITY_THRESHOLDS, levels=SEVERITY_LEVELS):
        self.thresholds = thresholds
        self.levels = levels

    def get_alert(self, pred, confidence):
        """
        Generate professional alert messages based on prediction and confidence.
        """
        if confidence > self.thresholds["warning"] and pred == 2:
            return "[CRITICAL] SEVERE CRASH DETECTED"
        elif pred == 2:
            return "[WARNING] Severe Crash Detected (Low Confidence)"
        elif confidence > self.thresholds["normal"] and pred == 1:
            return "[WARNING] Mild Impact Warning"
        elif pred == 1:
            return "[WARNING] Mild Impact Detected (Low Confidence)"
        elif pred == 3:
            return "[WARNING] Container Shift Detected"
        return "[OK] Normal Operation"

    def get_severity(self, confidence):
        """
        Get severity level and color based on confidence.
        """
        for level, (low, high, color) in self.levels.items():
            if low <= confidence < high:
                return level, color
        return "Unknown", "gray"

# For backward compatibility
_default_manager = AlertManager()

def get_alert(pred, confidence):
    return _default_manager.get_alert(pred, confidence)
