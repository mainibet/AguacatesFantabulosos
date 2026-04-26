import config
from machine import ADC, Pin #machine to access the hardware
import time

# ------------------------
# COLORS
# ------------------------
RED = "\033[31m"
BOLD =  "\033[1m"
RESET =  "\033[0m"

# ------------------------
# CONFIG
# ------------------------
THRESHOLD = config.THRESHOLD
SAMPLE_TIME = config.SAMPLE_TIME

mic = ADC(0)

# ------------------------
# CALIBRATION (simple average baseline)
# ------------------------
baseline = 0

for i in range(100):
    baseline += mic.read_u16()
    time.sleep(0.01)

baseline /= 100
last = 0

print("Baseline:", baseline)


# ------------------------
# BLE
# ------------------------
import uasyncio as asyncio
import aioble
import bluetooth

# BLE name
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-567812345678")
CHAR_UUID    = bluetooth.UUID("87654321-4321-8765-4321-876543214321")

# Create BLE service
ble = bluetooth.BLE()
ble.config(gap_name="MyESP32C3_Sonido")
aioble.core.ble.active(True)

# microchip BLE service
service = aioble.Service(SERVICE_UUID)
# service characteristic
char = aioble.Characteristic(
    service,
    CHAR_UUID,
    read=True,
    notify=True
)
aioble.register_services(service)

# ------------------------
# MONITORING LOOP
# ------------------------

# main loop
last = 0

#while True:
    #read sound level
  #  value = mic.read_u16()
    #filter value
 #   filterv = abs(value - baseline)
    
    #if is loud, send via BLE

#    if filterv > THRESHOLD:
       # msg = "ALERT: too loud! ruido={}\n".format(filterv)
      #  print("WARNING: too loud!", filterv)
        
        # send via BLE
     #   try:
    #        char.write(msg.encode("utf8"), notify=True)
#        except:
#            pass
   #      except Exception as e:      #debug
  #           print("BLE error:", e)  #debug

 #   last = value #is not using the filter now
    
#    time.sleep(SAMPLE_TIME)

# Bucle de prueba: envía alerta cada 5 segundos sin micrófono
async def main():
    print("Iniciando anuncio BLE...")
    # advertise() debe ser awaitable dentro de una corrutina
    async with await aioble.advertise(
        100000, # intervalo en microsegundos
        name="ESP32C3_Test",
        services=[SERVICE_UUID]
    ) as connection:
        print("Conectado a:", connection.device)
        while True:
            # Simulamos el envío cada 2 segundos
            char.write("Alerta!".encode("utf8")) # escribe el valor
            char.notify(connection, "Alerta!".encode("utf8")) # envía la notificación a la 
            print("Alerta enviada")
            await asyncio.sleep(2)

# Ejecutar el bucle principal
asyncio.run(main())
