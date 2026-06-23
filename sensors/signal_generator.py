# Synthetic sensor logic
import numpy as np
from config.settings import SAMPLE_RATE, WINDOW_DURATION

class SignalGenerator:
    def __init__(self, sample_rate=SAMPLE_RATE, duration=WINDOW_DURATION):
        self.sample_rate = sample_rate
        self.duration = duration

    def time_axis(self):
        return np.linspace(0, self.duration, self.sample_rate * self.duration)

    def _generate_brownian_noise(self, length, std=0.1):
        """Brownian (1/f^2) noise to simulate low-frequency hull/wave rumble."""
        return np.cumsum(np.random.normal(0, std, length)) * 0.1

    def generate_signal(self, label, wave_height=1.5, wind_speed=15.0, alignment_score=1.0):
        """
        Generate a signal with physics-based characteristics.
        - Low frequency: Hull sway from waves
        - Medium frequency: Engine vibration (Brownian noise)
        - High frequency: Transient impacts (Crashes)
        """
        if label not in (0, 1, 2, 3):
            raise ValueError(f"Invalid label: {label}. Must be 0, 1, 2, or 3.")
            
        t = self.time_axis()
        n_samples = len(t)
        
        # 1. Environmental Hull Sway (Low frequency oscillation)
        # Periodicity increases with wave height
        wave_freq = 0.2 + (wave_height / 20.0)
        sway = (wave_height * 0.1) * np.sin(2 * np.pi * wave_freq * t)
        
        # 2. Engine & Sea State Noise (Brownian + White noise)
        # Higher wind speed = more high-frequency surface 'chatter'
        noise_std = 0.05 + (wind_speed / 200.0)
        engine_vibration = self._generate_brownian_noise(n_samples, std=noise_std)
        jitter = np.random.normal(0, 0.02 * (1.1 - alignment_score), n_samples)
        
        base_signal = sway + engine_vibration + jitter

        if label == 0: # Normal
            return base_signal
        
        # 3. Transient Impact Model (Crashes/Shifts)
        impact_time = 2.5 # Center of window
        if label == 1: # Mild Impact (e.g., heavy wave slap)
            severity = 3.0 + (wave_height * 0.5)
            decay = 15.0
            ringing_freq = 8.0
        elif label == 2: # Severe Crash
            severity = 10.0 + (wave_height * 1.0)
            decay = 8.0
            ringing_freq = 12.0
        else: # Container Shift (label 3)
            severity = 5.0
            decay = 5.0
            ringing_freq = 4.0

        # Impact Envelope: Gaussian primary + Exponentially decaying ringing
        impact = severity * np.exp(-50 * (t - impact_time)**2)
        ringing = (severity * 0.3) * np.exp(-decay * np.maximum(0, t - impact_time)) * np.sin(2 * np.pi * ringing_freq * t)
        
        return base_signal + impact + ringing

# For backward compatibility
def generate_signal(label):
    return SignalGenerator().generate_signal(label)

def time_axis():
    return SignalGenerator().time_axis()
