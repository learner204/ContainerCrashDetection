import uuid
import time
from typing import Dict, Any, Optional
from threading import Lock

class VoyageManager:
    """
    Manages active voyages in a thread-safe manner.
    Allows the system to handle multiple concurrent simulations.
    """
    def __init__(self):
        self._voyages: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def create_voyage(self, voyage_data: Dict[str, Any]) -> str:
        """Creates a new voyage and returns its unique ID."""
        voyage_id = str(uuid.uuid4())
        with self._lock:
            self._voyages[voyage_id] = {
                **voyage_data,
                "id": voyage_id,
                "is_active": False,
                "start_time": None
            }
        return voyage_id

    def get_voyage(self, voyage_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a voyage by ID."""
        with self._lock:
            return self._voyages.get(voyage_id)

    def start_voyage(self, voyage_id: str) -> bool:
        """Marks a voyage as active."""
        with self._lock:
            if voyage_id in self._voyages:
                self._voyages[voyage_id]["is_active"] = True
                self._voyages[voyage_id]["start_time"] = time.time()
                return True
        return False

    def update_voyage(self, voyage_id: str, updates: Dict[str, Any]) -> bool:
        """Updates voyage parameters."""
        with self._lock:
            if voyage_id in self._voyages:
                self._voyages[voyage_id].update(updates)
                return True
        return False

    def remove_voyage(self, voyage_id: str):
        """Removes a voyage from the manager."""
        with self._lock:
            if voyage_id in self._voyages:
                del self._voyages[voyage_id]

# Singleton instance
voyage_manager = VoyageManager()
