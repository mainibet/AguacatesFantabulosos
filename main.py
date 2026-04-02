import con
from machine import ADC, Pin #machine to access the hardware
import time

# ------------------------
# CONFIG
# ------------------------

THRESHOLD = 25000

mic = ADC(26)  # GP26 = ADC0


# ------------------------
# WARMUP
# ------------------------
time.sleep(2)
    
# ------------------------
# CALIBRATION (simple average baseline)
# ------------------------
baseline = 0

for i in range(100):
    baseline += mic.read_u16()
    time.sleep(0.01)

baseline /= 100

print("Baseline:", baseline)
    

# ------------------------
# MONITORING LOOP
# ------------------------
while True:
    value = mic.read_u16()

    print(value)

    # Basic filter
    value = (value + baseline) / 2
    print(f"value after filter: {value}")
    # Alert
    if value > THRESHOLD:
        print("WARNING: too loud!")
    
    time.sleep(SAMPLE_TIME)
