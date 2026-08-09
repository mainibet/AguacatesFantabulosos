# Changelog (App)

## v0.3 (current)
Redesigned UI to match the Awareness Companion design reference

### Added
- Dashboard layout: status bar (connection + battery pills), header, three sensor cards and a recent-alerts section
- Threshold slider per sensor, set directly on the sensor scale (light, crowdness, noise)
- Recent alerts list and a full alert log popup (last 7 days)
- Line-drawn (lucide-style) icons replacing emoji glyphs
- Crowdness now estimates density from nearby BLE devices (ppl/m²) instead of dummy data

### Changed
- Color palette converted from the design's oklch tokens (dark indigo + mint/violet/sky tones)
- Light level (dark/normal/bright) mapped to the design's lux scale
- Event log is edge-triggered per sensor and records value + threshold
- Comments translated to English and split into titled sections

---

## v0.2
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
v0.4 → Local storage (SQLite event log)
v0.5 → Device communication (threshold sync via BLE)
v1.0 → Stable Bluetooth event system + real crowd sensor