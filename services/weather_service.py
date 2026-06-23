import requests
from typing import Dict

class WeatherService:
    """
    Fetches real-world marine weather data from Open-Meteo.
    Uses the Marine API for wave data and the Weather API for wind speed,
    since the Marine API does not serve wind_speed_10m.
    """
    MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def _safe_max(self, values, default=0.0):
        """Return the max of a list, filtering out None values."""
        filtered = [v for v in values if v is not None]
        return max(filtered) if filtered else default

    def fetch_marine_weather(self, lat: float, lng: float) -> Dict:
        """
        Fetch max wave height and wind speed for a specific coordinate.
        - Wave height: from Marine API (wave_height)
        - Wind speed: from Weather API (wind_speed_10m), since the
          Marine API always returns null for this variable.
        """
        max_wave = 1.5  # fallback default
        max_wind = 15.0  # fallback default

        # 1. Fetch wave data from the Marine API
        try:
            marine_params = {
                "latitude": lat,
                "longitude": lng,
                "hourly": "wave_height",
                "forecast_days": 7
            }
            response = requests.get(self.MARINE_URL, params=marine_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            wave_values = data.get("hourly", {}).get("wave_height", [])
            max_wave = self._safe_max(wave_values, default=1.5)
        except Exception as e:
            print(f"Error fetching marine wave data: {e}")

        # 2. Fetch wind speed from the Weather API
        try:
            weather_params = {
                "latitude": lat,
                "longitude": lng,
                "hourly": "wind_speed_10m",
                "forecast_days": 7
            }
            response = requests.get(self.WEATHER_URL, params=weather_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            wind_values = data.get("hourly", {}).get("wind_speed_10m", [])
            max_wind = self._safe_max(wind_values, default=15.0)
        except Exception as e:
            print(f"Error fetching weather wind data: {e}")

        return {
            "max_wave_height": float(max_wave),
            "max_wind_speed": float(max_wind)
        }

weather_service = WeatherService()
