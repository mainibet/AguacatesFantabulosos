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

    def start(self):
        threading.Thread(
            target=lambda: asyncio.run(self.run()),
            daemon=True
        ).start()

    async def run(self):
        while True:
            print("Scanning...")
            device = await BleakScanner.find_device_by_name("MyESP32C3_Sound")
            if not device:
                print("Not found, retrying...")
                await asyncio.sleep(2)
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

                    while True:
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
        # Devuelve 0=dark, 1=normal, 2=bright
        try:
            status = msg.split("LIGHT:")[1].split("|")[0]
            return {"DARK": 0, "NORMAL": 1, "BRIGHT": 2}.get(status, -1)
        except Exception:
            return None