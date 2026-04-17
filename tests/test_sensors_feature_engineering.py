import numpy as np

from sensors.feature_engineering import extract_features


def test_extract_features_returns_six_values():
    signal = np.array([1.0, 2.0, 3.0])
    features = extract_features(signal)
    assert len(features) == 6


def test_extract_features_known_signal_values():
    signal = np.array([1.0, 1.0, 1.0, 1.0])
    mean, std, max_v, min_v, rms, diff_sum = extract_features(signal)

    assert mean == 1.0
    assert std == 0.0
    assert max_v == 1.0
    assert min_v == 1.0
    assert rms == 1.0
    assert diff_sum == 0.0


def test_extract_features_handles_negative_numbers():
    signal = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    features = extract_features(signal)
    assert len(features) == 6
    assert features[2] == 2.0
    assert features[3] == -2.0
