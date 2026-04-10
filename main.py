
import config
from machine import ADC, Pin #machine to access the hardware
import time

# ------------------------
# CONFIG
# ------------------------
THRESHOLD = config.THRESHOLD
SAMPLE_TIME = config.SAMPLE_TIME

mic = ADC(26)  # GP26 = ADC0

# ------------------------
# COLORS
# ------------------------
RED = "\033[31m"
BOLD =  "\033[1m"
RESET =  "\033[0m"
# ------------------------
# WARMUP
# ------------------------
#time.sleep(2)
    
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
# MONITORING LOOP
# ------------------------
#print("listening..")
while True:
    value = mic.read_u16()

    #print(value)

    # Basic filter
    #value = (value + baseline) / 2
    filterv = abs(value - baseline)
    ##print(f"value after filter: {value}")
    # Alert
    #if abs(value - last) > 2000:
        #print("Value: "+ str(value) + "Filtered: "+ str(int(filterv)))

    if filterv > THRESHOLD:
        print(RED+"WARNING: too loud!" + RESET, filterv)
    
    last = value
    
    time.sleep(SAMPLE_TIME)

