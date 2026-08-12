# Awareness wearable

## 📌 Overview
A modular wearable that monitors noise, light, and crowd levels to help you stay in control of your environment.

## This version: v0.3 — Awareness Companion design (ESP32-C3 + Kivy)

This project reads analog sound signals using an ESP32-C3 Super Mini, broadcasts alerts via **Bluetooth Low Energy (BLE)** when the noise exceeds a configured threshold, and displays real-time data for noise, light, and crowd levels, along with battery status and configurable alert thresholds.

## Features
- Noise detection (BLE, traffic-light levels → dB)
- Light sensitivity (BLE, 3 levels mapped to lux)
- Crowd density estimated from nearby BLE devices (ppl/m²)
- Threshold slider per sensor, set directly on the sensor scale
- Recent alerts list + full alert log (last 7 days) in a bottom-sheet popup
- Connection and battery status pills in the top bar
- Event log with timestamped alerts (edge-triggered)

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

The ESP32-C3 notifies per sensor characteristic with `SENSOR:STATUS|COLOR|key=value`
payloads. The status is a **traffic-light level** (the design deliberately avoids
raw decibels — see `docs/decisions.md`).

| Characteristic | Message | Status (traffic light) |
|---|---|---|
| sound | `SOUND:LOUD\|Red\|noise=38345` | `QUIET` / `NORMAL` / `LOUD` |
| light | `LIGHT:DARK\|Green\|RAW:8000` | `DARK` / `NORMAL` / `BRIGHT` |
| crowd | `CROWD:LOW\|Green\|COUNT:0` | `LOW` / `MODERATE` / `HIGH` |
| battery | `BAT:85%\|V:3.9` | — |
| config (app → device) | `noise=60;light=800` | writable thresholds |

The value after `noise=`/`RAW=`/`COUNT=` is the raw sensor reading (display-only);
the app maps the status word onto the sensor scale (e.g. `LOUD` ≈ 95 dB) so the
threshold slider stays meaningful.

**Event-driven alerts:** the device does not stream continuously — it notifies
over BLE only when the reading exceeds the threshold configured in the app. The
app pushes its thresholds to the device through the config characteristic on
connect and whenever a slider changes.


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
│   ├── main.py                 ← App + RootLayout wiring and poll loop
│   ├── requirements.txt
│   ├── services/
│   │   ├── ble.py              ← BLE connection + message parser
│   │   ├── battery.py          ← OS battery monitor
│   │   ├── crowdness.py        ← Crowd density from nearby BLE devices
│   │   └── audio.py            ← Microphone capture + dB calculation
│   └── ui/
│       ├── theme.py            ← Design tokens (palette, radii, typography)
│       ├── data.py             ← Sensor registry + event log + formatters
│       ├── icons.py            ← Line-drawn (lucide-style) icons
│       ├── widgets.py          ← Card, Pill, IconTile, ThresholdSlider, Modal
│       └── dashboard.py        ← StatusBar, Header, SensorCard, alert lists
│
└── firmware/                   ← ESP32-C3 MicroPython
├── main.py
└── config.py
```

## Progress Documentation
- 📖 [User Guide](docs/user-guide.md)
- 📍 [Roadmap](docs/roadmap.md)
- 📈 [Progress](docs/progress.md)

## Versions
- current v0.3 — Awareness Companion design (current)
- v0.2 — Multi-sensor Kivy app with BLE
- v0.1 — Noise-only BLE prototype
Full changelog: [changelog](docs/changelog.md)


## 🚀 Future Improvements
- Real crowd sensor integration
- Log filtering and history view in app
- Adaptive thresholds
- Android/iOS packaging with Buildozer
