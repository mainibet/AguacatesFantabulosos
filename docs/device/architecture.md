# 🧠 Architecture

## 🔄 System Flow

Sound waves → Microphone → Analog voltage → ADC sampling → Digital value → Filtering → Decision logic → Event trigger
→ BLE Notification


### 📡 Signal Conversion

- Sound waves are converted into analog voltage by the microphone
- The ADC samples this voltage and produces a digital value

Formula:
`value = (Vin / Vref) * (2^bits - 1)`

## 📊 ADC Information

- ADC hardware resolution: 12-bit (0–4095)
- MicroPython returns values scaled to 16-bit (0–65535). Software representation, not physical resolution increase.
- Input pin: GPIO 0 (ADC0 channel on ESP32-C3).


## 🎛️ Signal Processing

The raw ADC signal can be noisy, so simple filtering is applied:

- Baseline calibration (ambient noise reference)
- Filtering: filterv = abs(value - baseline) identifies significant changes from the reference.
- Thresholding: Events are triggered only when the filtered value exceeds the configured config.THRESHOLD.
- Moving average (smoothing noise -future)
- Envelope detection (advanced peak detection - future)


## 🎧 Noise Levels (approximate calibration)

These values depend on the environment and microphone module:

- Silence → 3000 – 8000  
- Normal noise → 10000 – 25000  
- Loud noise → 30000 – 60000  

⚠️ These values are empirical and must be calibrated per device.

## Threshold

A fixed threshold is used to detect loud events:
`THRESHOLD = 1000`

If the signal exceeds this value, a noise event is triggered.

## 🔄 Sampling
The system reads the microphone every:
`100 ms (0.1 seconds)`

## 🧠 Software Architecture (Async BLE)
The system uses `asyncio` for non-blocking execution, allowing the 
BLE stack to manage connections in parallel with sensor monitoring.

- **Asynchronous Calibration**: The baseline is calculated during system 
    startup using asyncio.sleep(0.01) to avoid blocking the main event loop.
- **Parallel Tasks**: The system uses asyncio.gather to run the sound_monitor 
    task and the BLE advertising task simultaneously.
- **Communication**: 
    - Service: Custom BLE Service (UUID 1234...).
    - Characteristic: Notify-enabled characteristic (UUID 8765...) for real-time alerts.


## 📌 Assumptions

- Microphone outputs analog voltage
- Environment noise varies over time
- Threshold is manually calibrated per device
- Bluetooth-enabled client (mobile app) is required to subscribe to notifications for receiving alerts.
