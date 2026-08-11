import config
from machine import ADC
import uasyncio as asyncio
import aioble
import bluetooth
import utime
import gc #garbage collector (clean up RAM)
from machine import ADC, Pin
import network        # To activate WIFI radio
import esp32          # To activate sniffer mode
import hashlib        # To hash MAC addr

# ------------------------
# CONFIG BATTERY
# ------------------------
# initialize battery pin GPIO 3
# bat_adc = ADC(Pin(3))
bat_adc = ADC(Pin(config.BAT_GPIO_PIN))
bat_adc.atten(ADC.ATTN_11DB)

# ------------------------
# CONFIG SOUND
# ------------------------

#11dB (decibels) enable the pin to read full 0-3.3V range, not only 1.0V. (KY-037 delivers 3.3V)
mic = ADC(Pin(config.MIC_GPIO))
mic.atten(ADC.ATTN_11DB)

# ------------------------
# CONFIG LIGHT
# ------------------------
light_adc = ADC(Pin(config.LIGHT_GPIO))
light_adc.atten(ADC.ATTN_11DB)

# ------------------------
# CONFIG CROWDNESS (WI-FI SNIFFER)
# ------------------------

# Activate WIFI to listen
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# To store hased addr
seen_hashes = set()

def wifi_sniffer_callback(pkt):
    """Detecting crowdness ..."""
    if len(pkt) < 24:
        return  # Discard corrupted packets or packets shorter than the 802.11 header

    # Check if it is a 'Probe Request' (0x40) management frame
    frame_control = pkt[0]
    if (frame_control & 0xFC) == 0x40:
        mac_bytes = pkt[10:16]  # Extract the 6 bytes from the source MAC address
        
        # Random MAC filter: bit 1 of the first octet enabled indicates local administration (Smartphones)
        first_byte = mac_bytes[0]
        if bool(first_byte & 0x02):
            # Immediate anonymization with SHA-256 (MAC is not saved in plain text)
            mac_hash = hashlib.sha256(mac_bytes).digest()
            seen_hashes.add(mac_hash)

# ------------------------
# CONFIG BLE
# ------------------------

# Name the BLE
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-567812345678")
# Sound mail
CHAR_UUID    = bluetooth.UUID("87654321-4321-8765-4321-876543214321")
# Light mail
CHAR_LIGHT_UUID = bluetooth.UUID("87654321-4321-8765-4321-876543214323")
# Crwod mail
CHAR_CROWD_UUID = bluetooth.UUID("87654321-4321-8765-4321-876543214324")
# Battery mail
CHAR_BAT_UUID = bluetooth.UUID("87654321-4321-8765-4321-876543214322")

# Create BLE service
ble = bluetooth.BLE()
ble.config(gap_name="MyESP32C3_Sound")
aioble.core.ble.active(True)

# microchip BLE service
service = aioble.Service(SERVICE_UUID)

# service characteristic

# sound service
char = aioble.Characteristic(service, CHAR_UUID, read=True, notify=True)
# light service
char_light = aioble.Characteristic(service, CHAR_LIGHT_UUID, read=True, notify=True)
# crowd service
char_crowd = aioble.Characteristic(service, CHAR_CROWD_UUID, read=True, notify=True)
# battery service
char_bat = aioble.Characteristic(service, CHAR_BAT_UUID, read=True, notify=True)

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

def get_light_status(value):
    if value < config.LIGHT_DARK:
        return "DARK", "Green"
    elif value < config.LIGHT_MODERATE:
        return "NORMAL", "Yellow"
    else:
        return "BRIGHT", "Red"

def get_crowd_status(count):
    """[NUEVO] Evalúa el nivel de concurrencia de personas."""
    if count < config.CROWD_LOW:
        return "LOW", "Green"
    elif count < config.CROWD_MODERATE:
        return "MODERATE", "Yellow"
    else:
        return "HIGH", "Red"

# ------------------------
# TASKS
# ------------------------
# ------------- BATTERY ----------- #
async def battery_monitor(char_bat, connection):
    print("Battery monitor active")
    last_pct = -1
    
    while True:
        # 1. READ ADC and get an average
        raw_sum = 0
        for _ in range(10):
            raw_sum += bat_adc.read_u16()
            await asyncio.sleep_ms(5)
        raw_val = raw_sum / 10
        
        # 2. Convert digital value to a real battery voltage
        voltage = (raw_val / 65535.0) * config.BAT_REF * config.BAT_DIVIDER
        
        # 3. Calculate battery %
        pct = int(((voltage - config.BAT_VMIN) / (config.BAT_VMAX - config.BAT_VMIN)) * 100)
        pct = max(0, min(100, pct)) # To be sure is in the range 0% a 100%
        
        # 4. Report only if the % changed - saves energy
        if pct != last_pct:
            msg = f"BAT:{pct}%|V:{round(voltage, 2)}"
            print(msg)
            #timestamp for debug on shell
            print(f"[{utime.ticks_ms()/1000:.1f}s] {msg}")
            
            last_pct = pct #avoids local spam
            
            if connection is not None:
                try:
                    # register value on BLE
                    char_bat.write(msg.encode("utf8"))
                    char_bat.notify(connection)
                    last_pct = pct
                except Exception as e:
                    print("Error BLE Bat:", e)
        
        # Tasks sleeps per 30 secs
        await asyncio.sleep(config.BAT_INTERVAL)

# ------------- SOUND ----------- #

async def sound_monitor(char, connection):
    print("Sound monitor active")

    # Avoids overloading the BLE
    last_notification_time = 0
    last_category = ""

    while True:

        max_v = config.ADC_MIN_BIT
        min_v = config.ADC_MAX_BIT
    
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

# -------- LIGHT ------------------ #
async def light_monitor(char_light, connection):
    print("Light monitor active")
    last_notification_time = 0
    last_status = ""
    
    while True:
        light_val = light_adc.read_u16()
        status, color = get_light_status(light_val)
        current_time = utime.ticks_ms() / 1000
        
        if status != last_status or (current_time - last_notification_time >= config.LIGHT_COOLDOWN):
            msg = f"LIGHT:{status}|{color}|RAW:{light_val}"
            print(f"[{utime.ticks_ms()/1000:.1f}s] {msg}")
            
            last_status = status
            
            if connection is not None:
                try:
                    char_light.write(msg.encode("utf8"))
                    char_light.notify(connection)
                    last_notification_time = current_time
                except Exception as e:
                    print("Error BLE Light:", e)
            else:
                last_notification_time = current_time
                
        await asyncio.sleep(config.LIGHT_SAMPLE)

# -------------- CROWDNESS  -------------- #
async def crowd_monitor(char_crowd, connection):
    print("Crowdness monitor active")
    last_notification_time = 0
    last_status = ""
    
    # Start listening on WIFI (not every MicroPython build exposes the sniffer)
    if hasattr(esp32, "raw_dot11_sniffer"):
        esp32.raw_dot11_sniffer(wifi_sniffer_callback)
    else:
        print("Crowdness sniffer unavailable on this build — reporting 0")

    while True:
        await asyncio.sleep(config.CROWD_WINDOW_SEC)
        
        # Count unique hash durnig a period of time
        unique_count = len(seen_hashes)
        status, color = get_crowd_status(unique_count)
        current_time = utime.ticks_ms() / 1000
        
        if status != last_status or (current_time - last_notification_time >= config.CROWD_COOLDOWN):
            msg = f"CROWD:{status}|{color}|COUNT:{unique_count}"
            print(f"[{utime.ticks_ms()/1000:.1f}s] {msg}")
            
            last_status = status
            
            if connection is not None:
                try:
                    char_crowd.write(msg.encode("utf8"))
                    char_crowd.notify(connection)
                    last_notification_time = current_time
                except Exception as e:
                    print("Error BLE Crowd:", e)
            else:
                last_notification_time = current_time
        
        # clean accumulated hashes (saves RAM)
        seen_hashes.clear()

# -------- MAINTENANCE ------------ #
# run every 10 sec to clean up the RAM
async def system_maintenance():
    """Keeps RAM clean for continuous execution."""
    while True:
        gc.collect()
        await asyncio.sleep(10)

async def _guarded(coro, name):
    """Run one monitor; a crash is logged instead of killing the session."""
    try:
        await coro
    except Exception as e:
        print(f"Monitor {name} stopped:", e)

# ------------------------
# MAIN
# ------------------------
async def main():
    # 1. Calibration
    baseline = await get_calibration()

    while True: #to be able lto reconnect with the device
        print("Waiting for connection...")

        try:
            # 2. Manage connection
            async with await aioble.advertise(
                100000, name="MyESP32C3_Sound", services=[SERVICE_UUID] #mu = 100ms
            ) as connection:
                print("Connected to:", connection.device)

                # 3. Run all monitors until the central disconnects.
                # Tasks are guarded so a failing monitor cannot tear down
                # the connection, and cancelled on disconnect so no zombie
                # tasks keep spamming errors against a dead connection.
                tasks = [
                    asyncio.create_task(_guarded(sound_monitor(char, connection), "sound")),
                    asyncio.create_task(_guarded(battery_monitor(char_bat, connection), "battery")),
                    asyncio.create_task(_guarded(light_monitor(char_light, connection), "light")),
                    asyncio.create_task(_guarded(crowd_monitor(char_crowd, connection), "crowd")),
                    asyncio.create_task(system_maintenance()),
                ]
                await connection.disconnected()
                for t in tasks:
                    t.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
            print("Disconnected!")

        except Exception as e:
            print("Resetting BLE radio due to:", e)
            print("Disconnected! Re-opening advertisement...")
            await asyncio.sleep_ms(500)

asyncio.run(main())
