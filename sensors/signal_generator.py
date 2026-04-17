# Synthetic sensor logic
import numpy as np
from config.settings import SAMPLE_RATE, WINDOW_DURATION

class SignalGenerator:
    def __init__(self, sample_rate=SAMPLE_RATE, duration=WINDOW_DURATION):
        self.sample_rate = sample_rate
        self.duration = duration

    def time_axis(self):
        return np.linspace(0, self.duration, self.sample_rate * self.duration)

    def normal_signal(self, t):
        base = 0.3 * np.sin(2 * np.pi * 0.5 * t)
        noise = np.random.normal(0, 0.05, len(t))
        
        # Occasional small anomalies in normal signals (10% chance)
        if np.random.random() < 0.10:
            spike_idx = np.random.randint(0, len(t))
            noise[spike_idx] += np.random.choice([-0.3, 0.3])
        
        return base + noise

    def crash_signal(self, t, severity=8):
        severity_variation = severity * (1 + np.random.uniform(-0.2, 0.2))
        
        impact = severity_variation * np.exp(-20 * (t - 2.5)**2)
        vibration = 0.5 * np.sin(20 * t)
        
        noise_level = np.random.uniform(0.08, 0.15)
        noise = np.random.normal(0, noise_level, len(t))
        
        # Occasional sensor glitches (5% chance)
        if np.random.random() < 0.05:
            glitch_idx = np.random.randint(0, len(t))
            if np.random.random() < 0.5:
                noise[glitch_idx] += np.random.uniform(1.0, 2.0)
            else:
                noise[glitch_idx:glitch_idx+5] *= 0.1
        
        return impact + vibration + noise

    def generate_signal(self, label):
        t = self.time_axis()
        if label == 0:
            signal = self.normal_signal(t)
        elif label == 1:
            severity = np.random.uniform(2.5, 3.5)
            signal = self.crash_signal(t, severity=severity)
        elif label == 2:
            severity = np.random.uniform(7.0, 9.0)
            signal = self.crash_signal(t, severity=severity)
        else:
            severity = np.random.uniform(4.0, 6.0)
            signal = self.crash_signal(t, severity=severity) * np.sign(np.sin(t))
        
        # Add occasional sensor drift or calibration issues (3% chance)
        if np.random.random() < 0.03:
            drift = np.linspace(0, np.random.uniform(-0.2, 0.2), len(signal))
            signal = signal + drift
        
        return signal

# For backward compatibility
def generate_signal(label):
    return SignalGenerator().generate_signal(label)

def time_axis():
    return SignalGenerator().time_axis()
