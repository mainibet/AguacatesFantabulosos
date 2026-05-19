# Awareness wearable

## 📌 Overview
A modular wearable that monitors noise, light, and crowd levels to help you stay in control of your environment.

## This version: v0.2 — Multi-sensor App (ESP32-C3 + Kivy)

This project reads analog sound signals using an ESP32-C3 Super Mini, broadcasts alerts via **Bluetooth Low Energy (BLE)** when the noise exceeds a configured threshold, and displays real-time data for noise, light, and crowd levels, along with battery status and configurable alert thresholds.

## Features
- Noise detection
- Event log with timestamped alerts
- BLE notifications (status with auto-reconnect)
- Battery status with charge indicator
- Light sensitivity (BLE, 3 levels: dark / medium / bright)
- Crowd awareness (dummy data)

## 📦 Prerequisites

See full setup requirements here:
👉 [Prerequisites](docs/prerequisites.md)


## ⚙️ Hardware Setup
👉 [Hardware](docs/hardware.md)


## 🔌 Signal Flow

Microphone → Analog voltage → ADC (GND) → Digital value → Processing → Alert


## 🚀 Usage

### 💻 Running from Thonny (development mode)

1. Connect the ESP32-C3 board via USB
2. Open Thonny
3. Select interpreter:
   - MicroPython (ESP32-C3)

4. Open `main.py`
5. Click **Run**

➡ The code runs immediately on the microcontroller.


### 📟 Running on device (auto-start mode)

To make the program run automatically on boot:

1. In Thonny go to:
   File → Save as → MicroPython device

2. Save the file as: `main.py`
➡ The program will now start automatically when the board powers on.

## 📡 BLE Message Format

The ESP32-C3 sends semicolon-separated key=value pairs:

noise=72;light=1

| Key | Type | Values |
|---|---|---|
| `noise` | int | dB value (40–100) |
| `light` | int | 0=dark, 1=medium, 2=bright |


## 🧪 Calibration Guide
👉 [Calibration](docs/calibration.md)


## 🧠 Architecture

Technical explanation of how the system works:

👉 [Architecture](docs/architecture.md)


## 🧪 Calibration
At startup, the system measures ambient noise to compute a baseline reference value.


## 📁 Project Structure

```
project/
│
├── README.md
├── docs/
│
├── app/                        ← Kivy companion app
│   ├── main.py
│   ├── requirements.txt
│   ├── services/
│   │   ├── ble.py              ← BLE connection + parser
│   │   ├── battery.py          ← OS battery monitor
│   │   └── crowdness.py        ← Crowd dummy data
│   └── ui/
│       ├── theme.py            ← Colors and constants
│       ├── widgets.py          ← Card, NoiseBar, LogList
│       └── dashboard.py        ← BatteryCard, SensorMiniCard
│
└── firmware/                   ← ESP32-C3 MicroPython
├── main.py
└── config.py
```

## Progress Documentation
- 📍 [Roadmap](docs/roadmap.md)
- 📈 [Progress](docs/progress.md)

## Versions
- current v0.2 — Multi-sensor Kivy app (current)
- v0.1 — Noise-only BLE prototype
Full changelog: [changelog](docs/changelog.md)


## 🚀 Future Improvements
- Real crowd sensor integration
- Log filtering and history view in app
- Adaptive thresholds
- Android/iOS packaging with Buildozer
