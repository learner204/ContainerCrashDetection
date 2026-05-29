# Synthetic sensor logic
import numpy as np
from config.settings import SAMPLE_RATE, WINDOW_DURATION

class SignalGenerator:
    def __init__(self, sample_rate=SAMPLE_RATE, duration=WINDOW_DURATION):
        self.sample_rate = sample_rate
        self.duration = duration

    def time_axis(self):
        return np.linspace(0, self.duration, self.sample_rate * self.duration)

    def generate_signal(self, label, wave_height=1.5, wind_speed=15.0, alignment_score=1.0):
        """
        Generate a signal influenced by environmental and load factors.
        Higher waves/wind increase base vibration (noise).
        Lower alignment increases signal instability.
        """
        t = self.time_axis()
        
        # Base noise scaled by weather (High waves = more 'background' vibration)
        weather_noise_factor = (wave_height / 10.0) + (wind_speed / 100.0)
        base_noise_std = 0.05 + (0.2 * weather_noise_factor)
        
        # Stability factor (Poor alignment = more 'jitter' in normal motion)
        stability_factor = 1.1 - alignment_score # 0.1 (good) to 0.6 (bad)
        
        if label == 0: # Normal
            base = 0.3 * np.sin(2 * np.pi * 0.5 * t)
            noise = np.random.normal(0, base_noise_std * stability_factor, len(t))
            signal = base + noise
        elif label == 1: # Mild Impact
            severity = 2.5 + (2.0 * weather_noise_factor)
            signal = self.crash_signal(t, severity=severity, base_noise=base_noise_std)
        elif label == 2: # Severe Crash
            severity = 7.0 + (3.0 * weather_noise_factor)
            signal = self.crash_signal(t, severity=severity, base_noise=base_noise_std)
        elif label == 3: # Pre-Impact Warning (Instability)
            # Higher jitter and variance, but no sudden spike
            base = 0.5 * np.sin(2 * np.pi * 0.5 * t)
            # Instability increases over time in the window
            instability_ramp = np.linspace(1, 3, len(t))
            noise = np.random.normal(0, base_noise_std * 3 * stability_factor * instability_ramp, len(t))
            signal = base + noise
        else:
            severity = 4.0 + (2.0 * weather_noise_factor)
            signal = self.crash_signal(t, severity=severity, base_noise=base_noise_std) * np.sign(np.sin(t))
        
        return signal

    def crash_signal(self, t, severity=8, base_noise=0.1):
        impact = severity * np.exp(-20 * (t - 2.5)**2)
        vibration = 0.5 * np.sin(20 * t)
        noise = np.random.normal(0, base_noise, len(t))
        return impact + vibration + noise

# For backward compatibility
def generate_signal(label):
    return SignalGenerator().generate_signal(label)

def time_axis():
    return SignalGenerator().time_axis()
