# Thresholds, constants

SAMPLE_RATE = 100
WINDOW_DURATION = 5  # seconds

SEVERITY_THRESHOLDS = {
    "normal": 0.4,
    "warning": 0.7
}

EVENT_LABELS = {
    0: "Normal",
    1: "Mild Impact",
    2: "Severe Crash",
    3: "Unstable (Pre-Crash)"
}

SEVERITY_LEVELS = {
    "Normal": (0.0, 0.4, "green"),
    "Warning": (0.4, 0.7, "orange"),
    "Critical": (0.7, 1.0, "red")
}
