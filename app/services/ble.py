import asyncio
import threading
from bleak import BleakScanner, BleakClient

SERVICE_UUID    = "12345678-1234-5678-1234-567812345678"
CHAR_UUID       = "87654321-4321-8765-4321-876543214321"  # sound
CHAR_BAT_UUID   = "87654321-4321-8765-4321-876543214322"  # battery
CHAR_LIGHT_UUID = "87654321-4321-8765-4321-876543214323"  # light

class BLEMonitor:

    def __init__(self):
        self.connected  = False
        self.last_sound = None
        self.last_bat   = None
        self.last_light = None
        self._running   = False
        self._thread    = None
        self._pending   = None   # target device found by the scanner

    def start(self):
        if self._thread is not None:
            return
        self._running = True
        self._thread = threading.Thread(
            target=lambda: asyncio.run(self.run()),
            daemon=True
        )
        self._thread.start()

    def stop(self):
        """Stop the scan/connect loop and wait for the thread to finish,
        so the app can quit without crashing the interpreter."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None

    # ─────────────────────────────────────────────
    # SCANNER — wakes often so stop() returns quickly
    # ─────────────────────────────────────────────
    def _on_device(self, device, advertisement_data):
        name = advertisement_data.local_name or "" if advertisement_data else ""
        if name == "MyESP32C3_Sound" and self._pending is None:
            self._pending = device

    async def _find_device(self):
        """Scan until the wearable advertises; returns the device or None."""
        scanner = BleakScanner(detection_callback=self._on_device)
        await scanner.start()
        try:
            while self._running and self._pending is None:
                await asyncio.sleep(0.5)
        finally:
            await scanner.stop()
        device, self._pending = self._pending, None
        return device

    async def run(self):
        while self._running:
            print("Scanning...")
            device = await self._find_device()
            if not device:
                continue

            print("Found device, connecting...")
            try:
                async with BleakClient(device) as client:
                    self.connected = True
                    print("BLE connected")

                    def on_sound(_, data):
                        msg = data.decode()
                        print("SOUND:", msg)
                        self.last_sound = msg

                    def on_bat(_, data):
                        msg = data.decode()
                        print("BAT:", msg)
                        self.last_bat = msg

                    def on_light(_, data):
                        msg = data.decode()
                        print("LIGHT:", msg)
                        self.last_light = msg

                    await client.start_notify(CHAR_UUID,       on_sound)
                    await client.start_notify(CHAR_BAT_UUID,   on_bat)
                    await client.start_notify(CHAR_LIGHT_UUID, on_light)

                    while self._running:
                        await asyncio.sleep(1)

            except Exception as e:
                print("Connection error:", e)
                self.connected = False
                await asyncio.sleep(2)

    def parse_sound(self, msg):
        # "ALERT:LOUD|Red|noise=72"
        try:
            return int(msg.split("noise=")[1])
        except Exception:
            return None

    def parse_bat(self, msg):
        # "BAT:85%|V:3.9"
        try:
            return int(msg.split("BAT:")[1].split("%")[0])
        except Exception:
            return None

    def parse_light(self, msg):
        # "LIGHT:DARK|Green|RAW:8000"
        # Returns 0=dark, 1=normal, 2=bright
        try:
            status = msg.split("LIGHT:")[1].split("|")[0]
            return {"DARK": 0, "NORMAL": 1, "BRIGHT": 2}.get(status, -1)
        except Exception:
            return None