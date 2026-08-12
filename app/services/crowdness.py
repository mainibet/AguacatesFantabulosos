# services/crowdness.py — Crowd density estimation from nearby BLE devices.
#
# The wearable has no crowd sensor yet (roadmap Phase 3), so the app
# estimates how dense the space is by counting the unique BLE devices
# visible in a sliding time window, then maps that count to the design's
# people-per-m² scale (0–6).

import asyncio
import threading
import time

try:
    from bleak import BleakScanner
    _BLEAK_AVAILABLE = True
except ImportError:
    # iOS (kivy-ios) has no bleak — no BLE scanner, so no crowd estimate.
    _BLEAK_AVAILABLE = False

# The wearable itself advertises under this name — never counted as a crowd
DEVICE_NAME = "MyESP32C3_Sound"

# Time window (seconds) during which a device stays counted
SCAN_WINDOW_SECONDS = 20.0

# Calibration: observed devices per person per m² (tune after field tests)
DENSITY_PER_DEVICE = 0.9
MAX_DENSITY = 6.0


class CrowdnessMonitor:
    """
    Scans BLE advertisements on a background thread and exposes the current
    crowd density (ppl/m²) through update(). Returns None until the first
    device is seen.
    """

    def __init__(self):
        self._density = None
        self._seen = {}        # address → last seen timestamp
        self._running = False
        self._thread = None

    def start(self):
        """Launch the background scanner thread (idempotent)."""
        if not _BLEAK_AVAILABLE or self._thread is not None:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the scanner thread and wait for it to finish, so the app
        can quit without crashing the interpreter."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None

    def update(self):
        """Current density (0–6 ppl/m²) or None before the first reading."""
        return self._density

    # ─────────────────────────────────────────────
    # SCANNER
    # ─────────────────────────────────────────────
    def _on_device(self, device, advertisement_data):
        name = advertisement_data.local_name or "" if advertisement_data else ""
        if name == DEVICE_NAME:
            return  # ignore the wearable itself
        self._seen[device.address] = time.monotonic()
        self._prune()
        self._density = min(MAX_DENSITY, len(self._seen) * DENSITY_PER_DEVICE)

    def _prune(self):
        cutoff = time.monotonic() - SCAN_WINDOW_SECONDS
        for address in [a for a, t in self._seen.items() if t < cutoff]:
            del self._seen[address]

    def _run(self):
        while self._running:
            try:
                asyncio.run(self._scan_loop())
            except Exception as e:
                print("Crowdness scan error:", e)
                time.sleep(2)

    async def _scan_loop(self):
        scanner = BleakScanner(detection_callback=self._on_device)
        await scanner.start()
        try:
            steps = 0
            while self._running:
                # Wake up often so stop() can join the thread quickly
                await asyncio.sleep(1.0)
                steps += 1
                if steps >= int(SCAN_WINDOW_SECONDS):
                    steps = 0
                    self._prune()
        finally:
            await scanner.stop()
