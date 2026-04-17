from config.settings import (
    EVENT_LABELS,
    SAMPLE_RATE,
    SEVERITY_LEVELS,
    SEVERITY_THRESHOLDS,
    WINDOW_DURATION,
)


def test_core_settings_values():
    assert SAMPLE_RATE == 100
    assert WINDOW_DURATION == 5


def test_event_labels_and_thresholds_are_consistent():
    assert set(EVENT_LABELS.keys()) == {0, 1, 2, 3}
    assert SEVERITY_THRESHOLDS["normal"] < SEVERITY_THRESHOLDS["warning"]


def test_severity_levels_shape():
    for level_name, value in SEVERITY_LEVELS.items():
        low, high, color = value
        assert isinstance(level_name, str)
        assert 0.0 <= low < high <= 1.0
        assert isinstance(color, str)
