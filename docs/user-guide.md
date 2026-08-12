# Awareness Wearable — User Guide

## What this is

A small wearable (ESP32-C3 board) with three sensors — **noise**, **light** and
**crowdness** — that talks to a companion app over Bluetooth Low Energy (BLE).
The app runs on iPhone (kivy-ios) and macOS desktop.

The system is built around a **traffic-light** idea: instead of reporting raw
numbers, each sensor classifies its reading into one of three levels:

| Sensor | Green | Yellow | Red |
|---|---|---|---|
| Noise | QUIET | NORMAL | LOUD |
| Light | DARK | NORMAL | BRIGHT |
| Crowdness | LOW | MODERATE | HIGH |

The device sends the traffic-light label over BLE; the app decides when to
warn you based on the thresholds you set.

## How it works, end to end

1. **You set a threshold per sensor** with the slider on each card (noise on a
   dB-like scale, light on a lux-like scale, crowdness in people per m²).
2. The app **pushes your thresholds to the device** over BLE every time you
   change them (and on connect). The device uses them as its defaults until
   you push new ones.
3. The device samples continuously and **only notifies when a reading crosses
   above the threshold** — it does not stream data. The notification carries
   the traffic-light label (`SOUND:LOUD|Red|noise=…`, `LIGHT:BRIGHT|Red|RAW:…`,
   `CROWD:LOW|Green|COUNT:…`).
4. The app maps the label onto the sensor scale, logs an **alert event**, and
   marks the card **"Recent alert"** for **5 minutes**.
5. Alerts are **edge-triggered**: a sustained loud sound logs once when it
   crosses the threshold, not continuously. The event stays in the log;
   only the "Recent alert" badge expires.

## The status pill on each card

- **No alerts** — connected, nothing crossed the threshold recently
- **Recent alert** — the sensor reported an alert within the last 5 minutes
  (independent of the current threshold: raising the threshold doesn't erase
  what was already reported)
- **No signal** — device not connected

The top bar shows **Connected / Disconnected** and the **battery** level. The
connection pill reflects the real BLE state only — it is not tappable while a
real device connection is available.

## Threshold changes

- Moving a threshold **re-arms** the detector: if the current reading is
  already above the new threshold, an alert fires (with a 30-second guard so
  sliding a slider quickly doesn't flood the log with events).
- Example: lower the light threshold while the room is bright → the light
  card alerts immediately.

## Sensor timing (device side)

| Sensor | Sampling | Notification rule |
|---|---|---|
| Noise | 50 ms window (~20 Hz) | on level crossing, min 2 s apart |
| Light | 1 sample/s | on level crossing, min 3 s apart |
| Crowdness | 30 s accumulation window | once per window, min 5 s apart |
| Battery | every 30 s | only when the % changes |

## Using the iPhone app

- **No pairing needed** — BLE connects automatically; you don't pair the
  device in iPhone Settings.
- On first launch, **allow the Bluetooth permission** prompt.
- The device handles **one connection at a time**: if it is connected to the
  app on another device, it won't connect again until that app disconnects.
- Keep the device powered (USB cable is fine — BLE is wireless, range ~5–10 m).
- If the board ever goes silent after a power change (dead battery, replug),
  unplug/replug the USB cable or press its reset button.

## Known limitations

- **Crowdness sniffer**: this MicroPython build of the board has no Wi-Fi
  sniffer API, so the device always counts 0 devices → `LOW`. Real crowd
  numbers need a sniffer-capable firmware build or a dedicated sensor.
- **Battery reading**: the device reads the LiPo through a voltage divider.
  A deeply discharged battery reports `0%` even while charging — the battery
  math/wiring is a calibration item, not a BLE issue.
- **Crowdness on iOS** comes from the device's count (see sniffer note); the
  desktop app can also estimate crowdness from nearby BLE devices.

---

# Bug fixes log

Each entry: **where** (`App`, `Device` = ESP32 firmware, `Hardware` = physical
board/wiring) and a short description.

## App

- **[App] Noise value misread as dB** — the app treated the device's raw ADC
  amplitude (0–65535) as decibels, producing nonsense values like `38345 dB`.
  Now parses the traffic-light label (`LOUD`/`NORMAL`/`QUIET`).
- **[App] Fake units displayed** — event rows showed label-derived values
  (`95 dB`, `1000 lux`) as if measured. Rows now show the traffic-light word
  (`LOUD`, `BRIGHT`, …); the scale values remain internal for threshold logic.
- **[App] Demo alerts shown as real** — fake seeded alerts stayed in the log
  after connecting to the real device. Cleared on the first real connection.
- **[App] "Recent alert" erased by raising the threshold** — the badge
  re-checked the old alert against the current threshold. Now independent of
  the threshold, and the badge window is 5 minutes (was 60).
- **[App] Threshold change produced no alert** — lowering a threshold while
  the reading was already above it did nothing. The detector now re-arms and
  re-evaluates immediately (30 s throttle to avoid slider-drag spam).
- **[App] Crowdness never reported on iPhone** — no crowd data source existed
  on iOS. The app now subscribes to the device's crowd characteristic and
  maps `LOW/MODERATE/HIGH` → people per m².
- **[App] Manual connection pill** — the pill could be tapped to fake a
  connection. Disabled whenever a real BLE backend exists.
- **[App] Sensor icons upside down** — the icon renderer didn't flip the
  SVG y-axis. Fixed (verified geometrically).
- **[App] Sensor icons too bold** — stroke reduced from 1.3 to 1.0.
- **[App] No BLE on iOS** — the app had no iOS Bluetooth implementation
  (bleak is desktop-only). Added a CoreBluetooth backend (pyobjus) with the
  same interface: scan, connect, subscribe, read initial values, push
  thresholds.
- **[App] First readings missing on connect** — the device notifies only on
  edges, so nothing arrived until the first crossing. The app now reads the
  current values right after subscribing.
- **[iOS packaging] Bluetooth permission never prompted** — the app bundle
  lacked `NSBluetoothAlwaysUsageDescription` (iOS blocks Bluetooth access
  without it). Added.
- **[iOS packaging] CoreBluetooth.framework not linked** — added to the Xcode
  project.
- **[iOS packaging] Xcode build failed** — the sync script pointed at a
  non-existent folder, and Xcode's script sandbox blocked rsync. Fixed the
  source path/excludes and disabled sandboxing for the script phases.

## Device (ESP32 firmware)

- **[Device] Noise only sent when LOUD** — the firmware only notified on
  `ALERT:LOUD` and with a raw value. It now sends the traffic-light status for
  every level, consistently with light and crowd (`SOUND:LOUD|Red|noise=…`).
- **[Device] Thresholds not received from the app** — added a writable config
  characteristic; the device now gates its notifications on the app-set
  threshold (`noise=…;light=…`), with the firmware defaults as fallback.
- **[Device] Threshold change didn't re-notify** — lowering the threshold
  while a level was already above produced no notification. The edge detector
  re-arms on threshold change.
- **[Device] Crowd first reading delayed 30 s** — the crowd monitor slept
  through its accumulation window before sending anything. It now sends the
  initial reading immediately, then one per window.
- **[Device] Config write parse failed** — aioble needed `capture=True` for
  `written()` to return the payload (it returned the connection object).

## Hardware

- **[Hardware] Board hung after power loss** — after the LiPo died and
  charging started, the board went silent until reset. Replug USB / press
  reset. Not a code bug — power-state issue.
- **[Hardware] Battery reads 0% while charging** — the voltage-divider
  reading stays below the 3.0 V floor (`BAT:0%|V:1.75`) even on USB power.
  Open calibration item (divider/wiring or charge-state handling).
- **[Hardware] Crowd sniffer unavailable** — the flashed MicroPython build
  lacks `esp32.raw_dot11_sniffer`, so crowd always reports 0 devices (`LOW`).
  Open item: sniffer-capable firmware build or dedicated crowd sensor.
