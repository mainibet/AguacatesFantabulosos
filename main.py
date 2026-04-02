from machine import ADC, Pin #machine to access the hardware
import time

# ------------------------
# CONTEXT
# ------------------------

#read digital (0/1)
#write HIGH/LOW
#set-up pull-up/down

#ADC reads microphone voltage
#ADC range: 0 → 65535
#ADC with 12 bits
#ADC converts pin into analog sign I/
# read_u16() read voltag and return nb
#silent → 3000–8000
#normal noise → 10000–25000
#stornger noise → 30000–60000

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
    print(f{"value after filter: "; value)
    # Alert
    if value > THRESHOLD:
        print("WARNING: too loud!")
    
    time.sleep(0.1)
