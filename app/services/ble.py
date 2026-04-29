import asyncio
import threading
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "12345678-1234-5678-1234-567812345678"
CHAR_UUID = "87654321-4321-8765-4321-876543214321"


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

        print("Scanning...")

        devices = await BleakScanner.discover()

        target=None

        for d in devices:
            print(d.name, d.address)

            if d.name=="MyESP32C3_Sound":
                target=d
                break

        if not target:
            print("Device not found")
            return


        async with BleakClient(target.address) as client:

            self.connected=True
            print("BLE connected")


            def notification_handler(sender,data):
                msg=data.decode()
                print("NOTIFY:",msg)

                self.last_alert=msg


            await client.start_notify(
                CHAR_UUID,
                notification_handler
            )

            while True:
                await asyncio.sleep(1)