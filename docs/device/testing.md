# 🧪 Testing Procedures

## 1. BLE Connectivity Test
* **Objective**: Ensure the radio stack and `aioble` are operational.
* **Tool**: nRF Connect for Mobile.
* **Steps**:
    1. Reset the board.
    2. Scan for "MyESP32C3_Sound".
    3. Connect and subscribe to `0x8765...` (Notify/N).
* **Expected Result**: Mobile app shows the service and listens for notifications.

## 2. Sensor & Integration Test
* **Objective**: Verify analog readings and BLE alert trigger.
* **Tool**: Thonny Serial Console + nRF Connect.
* **Steps**:
    1. Run `main.py`.
    2. Generate sound spikes.
    3. Observe console output for "ALERT: ruido=..."
    4. Confirm mobile app receives the same alert via BLE notification.