# Awareness App Prototype (MVP)

## Overview
Desktop application built with Kivy to receive, display, and store **event-based environmental alerts** from the wearable device.

The app does NOT continuously stream sensor data.

It only receives meaningful events when thresholds are exceeded.

---

## Mock-up
### ▶️ Running the Prototype
`cd app/prototype
python3 -m http.server 8000`

`http://localhost:8000`

## Principles

- Local-first (all data stored on device)
- Privacy-focused (no cloud required)
- Event-driven (NOT continuous monitoring)
- Minimal cognitive load (calm UI by design)

---

## Features (v0.1)

- Receive alert events (via serial / Bluetooth future)
- Display threshold breach notifications
- Show event-based log history
- Store events locally using SQLite

---

## Data Storage

All event data is stored locally:
