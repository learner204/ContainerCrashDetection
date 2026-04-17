import numpy as np

def extract_features(signal):
    return [
        np.mean(signal),
        np.std(signal),
        np.max(signal),
        np.min(signal),
        np.sqrt(np.mean(signal**2)),
        np.sum(np.abs(np.diff(signal)))
    ]