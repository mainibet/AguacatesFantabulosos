# 🧠 Architecture

## 🔄 System Flow

Sound waves → Microphone → Analog voltage → ADC sampling → Digital value → Filtering → Decision logic → Event trigger

### 📡 Signal Conversion

### 📡 Signal Conversion

- Sound waves are converted into analog voltage by the microphone
- The ADC samples this voltage and produces a digital value

Formula:
`value = (Vin / Vref) * (2^bits - 1)`

## 📊 ADC Information

- ADC hardware resolution: 12-bit (0–4095)
- MicroPython returns values scaled to 16-bit (0–65535). Software representation, not physical resolution increase.
- Input pin: GP26 (ADC0 channel)


## 🎛️ Signal Processing

The raw ADC signal can be noisy, so simple filtering is applied:

- Baseline calibration (ambient noise reference)
- Moving average (smoothing noise)
- Envelope detection (advanced peak detection - future)


## 🎧 Noise Levels (approximate calibration)

These values depend on the environment and microphone module:

- Silence → 3000 – 8000  
- Normal noise → 10000 – 25000  
- Loud noise → 30000 – 60000  

⚠️ These values are empirical and must be calibrated per device.

## Threshold

A fixed threshold is used to detect loud events:
`THRESHOLD = 25000`

If the signal exceeds this value, a noise event is triggered.

## 🔄 Sampling
The system reads the microphone every:
`100 ms (0.1 seconds)`

## 📌 Assumptions

- Microphone outputs analog voltage
- Environment noise varies over time
- Threshold is manually calibrated per device
