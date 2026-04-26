## Changelog - Device Firmware

### v0.2.0 - Bluetooth Low Energy Integration (Current)
- **Firmware**: Migrated from síncronous `while` loop to `asyncio` architecture.
- **Communication**: Implemented `aioble` for real-time alerting.
- **Sensor**: ESP32-C3 ADC integration for microphone (GPIO 0).
- **Calibration**: Added non-blocking asynchronous calibration at startup.

### v0.1.0 - Initial ADC Prototype
- Basic threshold detection using RP2040.