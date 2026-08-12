# Changelog (App)

## v0.3 (current)
Redesigned UI to match the Awareness Companion design reference

### Added
- Dashboard layout: status bar (connection + battery pills), header, three sensor cards and a recent-alerts section
- Threshold slider per sensor, set directly on the sensor scale (light, crowdness, noise)
- Recent alerts list and a full alert log popup (last 7 days)
- Line-drawn (lucide-style) icons replacing emoji glyphs
- Crowdness now estimates density from nearby BLE devices (ppl/m²) instead of dummy data
- iOS BLE backend (CoreBluetooth via pyobjus) — scan, connect, subscribe, read initial values, threshold push
- Threshold sync to the device via the config characteristic (pushed on connect and on slider change)

### Changed
- Color palette converted from the design's oklch tokens (dark indigo + mint/violet/sky tones)
- Light level (dark/normal/bright) mapped to the design's lux scale
- Event log is edge-triggered per sensor and records value + threshold
- Comments translated to English and split into titled sections
- Event rows show the traffic-light word (LOUD / BRIGHT / …) instead of label-derived units
- "Recent alert" badge window shortened 60 → 5 minutes and made threshold-independent
- Manual connection pill disabled while a real BLE backend exists

### Fixed
- Noise value misread as dB: the app treated the device's raw ADC amplitude (0–65535) as decibels — now parses the traffic-light label
- Seeded demo alerts persisted after connecting to the real device — cleared on the first real connection
- Raising a threshold erased existing "Recent alert" badges — alerts stay until they expire
- Lowering a threshold while the reading was already above produced no alert — detector re-arms and re-evaluates immediately (30 s throttle against slider-drag spam)
- Crowdness had no data source on iOS — subscribes to the device crowd characteristic (LOW/MODERATE/HIGH → ppl/m²)
- Sensor icons rendered upside down (SVG y-axis was not flipped) and too bold (stroke 1.3 → 1.0)
- First readings were missed on connect because the device notifies on edges only — the app now reads the current values right after subscribing
- iOS bundle lacked `NSBluetoothAlwaysUsageDescription` (Bluetooth access silently blocked) — added
- CoreBluetooth.framework was not linked in the Xcode project — added
- Xcode build failed: sync script pointed at a non-existent folder and Xcode's script sandbox blocked rsync — fixed source/excludes and disabled sandboxing for script phases

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
v1.0 → Stable Bluetooth event system + real crowd sensor