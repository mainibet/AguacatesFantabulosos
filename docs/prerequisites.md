## 📦 Prerequisites

### 🔧 Hardware
- 1x ESP32-C3-based board (e.g. ESP32-C3 super mini)
- 1x Microphone sensor module (analog output)
- 1x Breadboard
- Jumper wires (male-to-male)
- USB cable (for power + programming)
- (Optional) LED + resistor (for testing alerts)

---

### 💻 Software
- Python 3.x (for local development tools)
- Thonny IDE (recommended for MicroPython development)
- MicroPython firmware installed on ESP32-C3

---

### ⚙️ Microcontroller firmware
- **Target**: MicroPython for ESP32-C3
- **Installation**: Flashed using Thonny IDE or `esptool.py`
- **Official Download**: [MicroPython ESP32-C3 Firmware](https://micropython.org/download/ESP32_GENERIC_C3/)

---

### 💻 Development Mode
1. Ensure `aioble` is installed: *Tools → Manage Packages → aioble → Install*.
2. Run `main.py` via Thonny.
3. Monitor BLE alerts in real-time.

### 📟 Deployment
1. Save `main.py` and `config.py` to **MicroPython device (ESP32)**.
2. The code runs on power-up, initiating an `asyncio` loop for sensor monitoring and BLE advertising.

---

### 🧠 Knowledge (basic level)
- Basic Python syntax (loops, variables, print)
- Basic understanding of circuits (VCC, GND, signal pins)