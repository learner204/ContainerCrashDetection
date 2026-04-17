from unittest.mock import Mock

import numpy as np
import pytest

from services.detector import CrashDetector


@pytest.fixture
def detector_with_mocks(monkeypatch):
    mock_model = Mock()
    mock_model.predict.return_value = np.array([1])
    mock_model.predict_proba.return_value = np.array([[0.1, 0.85, 0.03, 0.02]])
    mock_conn = Mock()
    mock_conn.execute = Mock()
    mock_conn.commit = Mock()
    mock_conn.close = Mock()

    class DummyDBManager:
        def __init__(self):
            self.conn = mock_conn

        def get_connection(self):
            return self.conn

    monkeypatch.setattr("services.detector.joblib.load", lambda _p: mock_model)
    monkeypatch.setattr("services.detector.DatabaseManager", DummyDBManager)

    detector = CrashDetector("fake-model.pkl")
    return detector, mock_model, mock_conn


def test_predict_returns_python_types_and_clamped_confidence(detector_with_mocks, monkeypatch):
    detector, _mock_model, _mock_conn = detector_with_mocks

    monkeypatch.setattr("services.detector.np.random.normal", lambda _m, _s: 0.0)
    monkeypatch.setattr("services.detector.np.random.random", lambda: 0.99)

    signal = np.ones(500)
    pred, conf = detector.predict(signal)

    assert isinstance(pred, int)
    assert isinstance(conf, float)
    assert 0.30 <= conf <= 0.98


def test_log_event_rejects_none_values(detector_with_mocks):
    detector, _, _mock_conn = detector_with_mocks

    with pytest.raises(ValueError):
        detector.log_event(None, 0.5, "alert")

    with pytest.raises(ValueError):
        detector.log_event(1, None, "alert")


def test_log_event_writes_to_db(detector_with_mocks):
    detector, _, conn = detector_with_mocks

    detector.log_event(2, 0.9, "critical")

    conn.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()


def test_model_load_error_bubbles_up(monkeypatch):
    def raise_missing(_path):
        raise FileNotFoundError("missing")

    monkeypatch.setattr("services.detector.joblib.load", raise_missing)

    with pytest.raises(FileNotFoundError):
        CrashDetector("missing.pkl")
