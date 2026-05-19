import asyncio
import threading
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "12345678-1234-5678-1234-567812345678"
CHAR_UUID = "87654321-4321-8765-4321-876543214321"

# Light levels
LIGHT_LEVELS = {
    0: ("Dark",   "ok"),
    1: ("Medium", "warning"),
    2: ("Bright", "alert"),
}

class BLEMonitor:

    def __init__(self):
        self.connected=False
        self.last_alert=None

    def start(self):
        threading.Thread(
            target=lambda: asyncio.run(self.run()),
            daemon=True
        ).start()

    async def run(self):

        while True:
            print("Scanning...")

            device = await BleakScanner.find_device_by_name(
                "MyESP32C3_Sound"
            )

            if not device:
                print("Not found, retrying...")
                await asyncio.sleep(2)
                continue

            print("Found device, connecting...")

            try:
                async with BleakClient(device) as client:

                    self.connected = True
                    print("BLE connected")

                    def notification_handler(_, data):
                        msg = data.decode()
                        print("NOTIFY:", msg)
                        self.last_alert = msg

                    await client.start_notify(
                        CHAR_UUID,
                        notification_handler
                    )

                    while True:
                        await asyncio.sleep(1)

            except Exception as e:
                print("Connection error:", e)
                self.connected = False
                await asyncio.sleep(2)

    def parse_ble(self,msg: str) -> dict:
        result = {}
        for part in msg.split(";"):
            if "=" in part:
                key, _, val = part.partition("=")
                try:
                    result[key.strip()] = float(val.strip())
                except ValueError:
                    pass
        return result