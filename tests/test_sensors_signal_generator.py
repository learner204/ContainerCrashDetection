import numpy as np

from config.settings import SAMPLE_RATE, WINDOW_DURATION
from sensors.signal_generator import SignalGenerator, generate_signal, time_axis


EXPECTED_LENGTH = SAMPLE_RATE * WINDOW_DURATION


def test_time_axis_length_and_bounds():
    sg = SignalGenerator()
    t = sg.time_axis()
    assert len(t) == EXPECTED_LENGTH
    assert t[0] == 0.0
    assert t[-1] == WINDOW_DURATION


def test_generate_signal_all_labels_have_expected_length():
    np.random.seed(123)
    sg = SignalGenerator()
    for label in [0, 1, 2, 3]:
        signal = sg.generate_signal(label)
        assert len(signal) == EXPECTED_LENGTH


def test_module_level_helpers_delegate():
    np.random.seed(7)
    t = time_axis()
    signal = generate_signal(0)
    assert len(t) == EXPECTED_LENGTH
    assert len(signal) == EXPECTED_LENGTH
