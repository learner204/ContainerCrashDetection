from collections import deque

from utils.helpers import rolling_buffer


def test_rolling_buffer_returns_deque():
    buf = rolling_buffer(3)
    assert isinstance(buf, deque)
    assert buf.maxlen == 3


def test_rolling_buffer_enforces_maxlen():
    buf = rolling_buffer(3)
    for i in range(6):
        buf.append(i)
    assert list(buf) == [3, 4, 5]
