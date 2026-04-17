import numpy as np
from services.detector import CrashDetector

class StreamingDetector:
    def __init__(self, detector=None):
        self.detector = detector or CrashDetector()

    def detect_from_buffer(self, buffer):
        if len(buffer) < buffer.maxlen:
            return None, None
        signal = np.array(buffer)
        return self.detector.predict(signal)

# For backward compatibility
def detect_from_buffer(buffer):
    return StreamingDetector().detect_from_buffer(buffer)
