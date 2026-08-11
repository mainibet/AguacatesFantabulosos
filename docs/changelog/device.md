
### v0.3.0 - Connection hardening (current)
- **Crowdness**: Guarded `esp32.raw_dot11_sniffer` behind a capability check — builds without the sniffer API no longer crash the BLE session (report 0 instead).
- **BLE lifecycle**: Monitor tasks are now guarded and cancelled on disconnect — a failing monitor can no longer tear down the connection, and no zombie tasks keep spamming errors against a dead connection after the client leaves.
- **Reconnect**: Verified the device re-advertises after every disconnect (loop was previously unreachable when the monitors stayed alive).

### v0.2.1 - Battery & Light Sensor
- **Battery**: Voltage-divider ADC (GPIO 3) reads the LiPo voltage, converts it to a percentage (Vmax 4.2 V / Vmin 3.0 V), and sends `BAT:xx%|V:x.xx` over BLE (averaged reads, notify only when the % changes, 30 s interval).
- **Light**: LDR on GPIO 1 classified into a 3-level traffic light (DARK / MODERATE / BRIGHT), sent as `LIGHT:status|color|RAW:value` over BLE with a cooldown between same-level notifications.

### v0.2.0 - Bluetooth Low Energy Integration
- **Firmware**: Migrated from síncronous `while` loop to `asyncio` architecture.
- **Communication**: Implemented `aioble` for real-time alerting.
- **Sensor**: ESP32-C3 ADC integration for microphone (GPIO 0).
- **Calibration**: Added non-blocking asynchronous calibration at startup.

### v0.1.0 - Initial ADC Prototype
- Basic threshold detection using RP2040.