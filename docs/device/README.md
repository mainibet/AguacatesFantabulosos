# Device Firmware (RP2040 - MicroPython)

## Overview
This module runs on the wearable device and handles sensor input, signal processing, and event generation.

---

## Current Version: Noise Detection System

The system reads analog audio signals using ADC (GP26) and detects when thresholds are exceeded.

---

## Signal Flow

Microphone → Analog voltage → ADC (GP26) → Digital processing → Threshold evaluation → Event trigger

---

## Calibration

At startup, the device measures ambient noise to establish a baseline reference.

---

## Hardware Setup

See: `docs/hardware.md`

---

## Running the Device

### Development (Thonny)
1. Connect RP2040 via USB
2. Open Thonny
3. Run `main.py`

### Production Mode
Save `main.py` directly to the device for auto-execution on boot

---

## Features

- Noise detection (active)
- Light detection (planned)
- Crowd detection (planned)

---

## Output

The device does NOT stream continuous data.

It only emits events when thresholds are exceeded.