# Changelog (App)

## v0.2 (current)
Multi-sensor Kivy app with BLE integration

### Added
- BLE connection to ESP32-C3 with auto-reconnect
- Real-time noise level display with configurable threshold
- Light level monitoring via BLE (dark / medium / bright)
- Crowd awareness card (dummy data)
- Battery status with charge indicator and color coding
- BLE message parser (`noise=72;light=1` format)
- Connected / Disconnected badge in header

### Changed
- UI rebuilt in Kivy from HTML prototype
- Project structure split into `services/` and `ui/` modules

---

## v0.1
Event UI prototype (HTML + Kivy layout concept) + threshold-based alerts (simulated)

### Added
- Noise event detection
- Basic alert UI
- Local event logging

### Notes
- Prototype-based UI
- No BLE yet

**upcoming:**
v0.2 → Kivy UI implementation + calibration display
v0.3 → Local storage (SQLite event log)
v0.4 → Device communication (Serial → BLE migration)
v1.0 → Stable Bluetooth event system + multi-event support (noise/light/crowd)