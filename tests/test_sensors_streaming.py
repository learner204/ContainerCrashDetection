from sensors import streaming as streaming_module


def test_stream_signal_repeats_generated_signal(monkeypatch):
    monkeypatch.setattr(streaming_module, "generate_signal", lambda _label: [10, 20, 30])

    stream = streaming_module.stream_signal(0)
    observed = [next(stream) for _ in range(7)]

    assert observed == [10, 20, 30, 10, 20, 30, 10]
