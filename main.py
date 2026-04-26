import config
from machine import ADC
import uasyncio as asyncio
import aioble
import bluetooth

# ------------------------
# CONFIG SOUND
# ------------------------
THRESHOLD = config.THRESHOLD
SAMPLE_TIME = config.SAMPLE_TIME
mic = ADC(0)

# ------------------------
# CONFIG BLE
# ------------------------

# Name the BLE
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-567812345678")
CHAR_UUID    = bluetooth.UUID("87654321-4321-8765-4321-876543214321")

# Create BLE service
ble = bluetooth.BLE()
ble.config(gap_name="MyESP32C3_Sound")
aioble.core.ble.active(True)

# microchip BLE service
service = aioble.Service(SERVICE_UUID)

# service characteristic
char = aioble.Characteristic(service, CHAR_UUID, read=True, notify=True)
aioble.register_services(service)

# ------------------------
# CALIBRATION
# ------------------------
async def get_calibration():
    print("Calibrating ...")
    baseline = 0
    for i in range(100):
        baseline += mic.read_u16()
        await asyncio.sleep(0.01)
    baseline /= 100
    print("Baseline:", baseline)
    return baseline

# ------------------------
# TASKS
# ------------------------
async def sound_monitor(char, connection, baseline):
    print("Sound monitor active")
    while True:
        # read sound level
        value = mic.read_u16()
        # filter value
        filterv = abs(value - baseline)

        # if is loud, send via BLE
        if filterv > THRESHOLD:
            msg = f"ALERT: ruido={int(filterv)}"
            print(msg)
            
            # Only try to send if there is a connection
            if connection is not None:
                try:
                    char.write(msg.encode("utf8"), send_update=False)
                    char.notify(connection, msg.encode("utf8"))
                except Exception as e:
                    print("Error BLE:", e)
                    connection = None # Marcamos conexión como perdida
            else:
                print("No hay dispositivo conectado, alerta omitida.")
                
        await asyncio.sleep(SAMPLE_TIME)

# ------------------------
# MAIN
# ------------------------
async def main():
    # 1. Calibration
    baseline = await get_calibration()
    
    while True: #to be able lto reconnect with the device
        print("Waiting for connection...")
        
        # 2. Manage connection
        async with await aioble.advertise(
            100000, name="MyESP32C3_Sound", services=[SERVICE_UUID] #mu = 100ms
        ) as connection:
            print("Connected to:", connection.device)
            
            # 3.Manage all tasks in paralel
            await asyncio.gather(sound_monitor(char, connection, baseline)
                                 # light_monitor(char_light, connection)  <-- Add here in the future
                                 )
        print("Disconnected!")

asyncio.run(main())
