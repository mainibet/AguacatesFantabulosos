import random

class CrowdnessMonitor:
    """
    Dummy data.
    """

    def __init__(self):
        self._value = 40.0

    def update(self):
        """Soft noise. Returns float 0–100."""
        self._value = max(0.0, min(100.0, self._value + random.uniform(-1, 1)))
        return round(self._value, 1)