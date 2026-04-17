from collections import deque

from services.streaming_detectors import StreamingDetector


class StubDetector:
    def predict(self, _signal):
        return 2, 0.88


def test_detect_from_buffer_requires_full_buffer():
    detector = StreamingDetector(detector=StubDetector())
    buf = deque([1, 2], maxlen=5)
    pred, conf = detector.detect_from_buffer(buf)
    assert pred is None
    assert conf is None


def test_detect_from_buffer_returns_prediction_for_full_buffer():
    detector = StreamingDetector(detector=StubDetector())
    buf = deque([1, 2, 3, 4, 5], maxlen=5)
    pred, conf = detector.detect_from_buffer(buf)
    assert pred == 2
    assert conf == 0.88
