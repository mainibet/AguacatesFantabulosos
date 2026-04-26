# Awareness wearable

## 📌 Overview
A modular wearable that monitors noise, light, and crowd levels to help you stay in control of your environment.

## This version: 🎤 Noise Detection System (ESP32-C3 + MicroPython)

his project reads analog sound signals using an ESP32-C3 Super Mini, computes a baseline noise level at startup, 
and broadcasts alerts via **Bluetooth Low Energy (BLE)** when the noise exceeds a configured threshold.

## Features
- Noise detection
- BLE notifications
- Light sensitivity (upcoming)
- Crowd awareness (upcoming)

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


## 🧪 Calibration Guide
👉 [Calibration](docs/calibration.md)


## 🧠 Architecture

Technical explanation of how the system works:

👉 [Architecture](docs/architecture.md)


## 🧪 Calibration
At startup, the system measures ambient noise to compute a baseline reference value.


## 🚀 Future Improvements
- Moving average filter
- Envelope detection (audio smoothing)
- Adaptive thresholding
- Bluetooth alert system


## 📁 Project Structure

```
project/
│
├── README.md
├── main.py
├── config.py
│
└── docs/
    ├── prerequisites.md
    ├── hardware.md
    ├── calibration.md
    ├── architecture.md
    ├── project_structure.md
    ├── testing.md
    └── changelog.md
```
## Progress Documentation
- 📍 [Roadmap](docs/roadmap.md)
- 📈 [Progress](docs/progress.md)

## Versions
current v0.1 (more versions: [changelog](docs/changelog.md))