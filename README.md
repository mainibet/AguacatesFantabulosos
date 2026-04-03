# Awareness wearable

## 📌 Overview
A modular wearable that monitors noise, light, and crowd levels to help you stay in control of your environment.

## This version: 🎤 Noise Detection System (RP2040 + MicroPython)

This project reads analog sound signals from a microphone using an ADC pin on an RP2040 microcontroller and detects noise levels based on configurable thresholds.

## Features
- Noise detection -> current version
- Light sensitivity (upcoming)
- Crowd awareness (upcoming)

## 📦 Prerequisites

See full setup requirements here:
👉 [Prerequisites](docs/prerequisites.md)


## ⚙️ Hardware Setup
👉 [Hardware](docs/hardware.md)


## 🔌 Signal Flow

Microphone → Analog voltage → ADC (GP26) → Digital value → Processing → Alert


## 🚀 Usage

### 💻 Running from Thonny (development mode)

1. Connect the RP2040 board via USB
2. Open Thonny
3. Select interpreter:
   - MicroPython (Raspberry Pi Pico / RP2040)

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
    └── changelog.md
```
## Progress Documentation
- 📍 [Roadmap](docs/roadmap.md)
- 📈 [Progress](docs/progress.md)

## Versions
current v0.1 (more versions: [changelog](docs/changelog.md))