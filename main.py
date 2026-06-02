import config
from machine import ADC
import uasyncio as asyncio
import aioble
import bluetooth
import utime
import gc #garbage collector (clean up RAM)

# ------------------------
# CONFIG SOUND
# ------------------------

#11dB (decibels) enable the pin to read full 0-3.3V range, not only 1.0V. (KY-037 delivers 3.3V)
#
mic = ADC(0)
mic.atten(ADC.ATTN_11DB)

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

# -------------------------
# TRAFFIC LIGHT PROCESSING
# -------------------------

# amplitude is the volume measure
def get_noise_status(amplitude):
    """Classifies sound based on thresholds."""
    if amplitude < config.SOUND_QUIET:
        return "QUIET", "Green"
    elif amplitude < config.SOUND_MODERATE:
        return "NORMAL", "Yellow"
    else:
        return "LOUD", "Red"

# ------------------------
# TASKS
# ------------------------
async def sound_monitor(char, connection):
    print("Sound monitor active")

    # Avoids overloading the BLE
    last_notification_time = 0
    last_category = ""

    while True:

        max_v = ADC_MIN_BIT
        min_v = ADC_MAX_BIT
    
        # 50ms window loop
        sample_start = utime.ticks_ms()
        while utime.ticks_diff(utime.ticks_ms(), sample_start) < 50:
            val = mic.read_u16() #read sound level
            if val > max_v: max_v = val
            if val < min_v: min_v = val
        
        # Calculate real wave amplitude
        amplitude = max_v - min_v
        category, color = get_noise_status(amplitude)

        current_time = utime.ticks_ms() / 1000 #1000 to convert it into sec

        if category != last_category or (current_time - last_notification_time >= config.SOUND_COOLDOWN):
            if category == "LOUD": # Triggers alert based on your requirements
                msg = f"ALERT:{category}|{color}|noise={int(amplitude)}"
                print(msg)
                
                if connection is not None:
                    try:
                        char.write(msg.encode("utf8"))
                        char.notify(connection)
                        last_notification_time = current_time
                        last_category = category
                    except Exception as e:
                        print("Error BLE:", e)
                        connection = None
                else:
                    print("No device connected, alert skipped.")

        # Yield CPU control back to the async loop for BLE reliability
        await asyncio.sleep(config.SAMPLE_TIME)


# run every 10 sec to clean up the RAM
async def system_maintenance():
    """Keeps RAM clean for continuous execution."""
    while True:
        gc.collect()
        await asyncio.sleep(10)

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
            await asyncio.gather(sound_monitor(char, connection),
                                 system_maintenance()
                                 # light_monitor(char_light, connection)  <-- Add here in the future
                                 )
        print("Disconnected!")

asyncio.run(main())
