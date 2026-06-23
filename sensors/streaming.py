# NOTE: This module is currently unused in the project but kept for potential future streaming enhancements.
from sensors.signal_generator import generate_signal

def stream_signal(label):
    """
    Generator that yields sensor values continuously.
    Loops through the generated signal repeatedly for continuous streaming.
    """
    signal = generate_signal(label)
    while True:
        for value in signal:
            yield value
