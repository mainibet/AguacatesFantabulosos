# Awareness App Prototype (HTML Mockup)

## ⚠️ Important

This is **NOT the final application**.

This prototype is a **static HTML mockup** used to simulate the behavior and design of the Awareness App.

It does **not implement real functionality, device communication, or data persistence**.

---

## 📌 Overview

This prototype represents the **conceptual design** of a desktop application intended to:

* Receive environmental alerts from a wearable device
* Display meaningful events (not raw sensor data)
* Provide a calm and minimal user experience

The real application will be built with **Kivy**, but this version exists only to validate UI/UX decisions.

---

## 🎯 Purpose

The goal of this prototype is to:

* Explore interface layout and interaction
* Validate event-based UX (alerts, logs, feedback)
* Test the "feel" of the system before implementation

---

## 🚀 Running the Prototype

From the project root:

```bash
cd app/prototype
python3 -m http.server 8000
```

Then open in your browser:

```
http://localhost:8000
```

---

## 🧪 What This Prototype Simulates

* Event-based alerts (e.g. noise threshold exceeded)
* Visual feedback for environmental changes
* Conceptual event log interface

---

## ❌ What This Prototype Does NOT Do

* No real sensor input
* No Serial or Bluetooth communication
* No SQLite or persistent storage
* No backend or application logic

---

## 🔄 Differences vs Final Application

| Prototype        | Final App (planned)        |
| ---------------- | -------------------------- |
| Static HTML      | Kivy application           |
| Simulated events | Real device data           |
| No storage       | SQLite event storage       |
| No connectivity  | BLE / device communication |

---

## 🧠 Design Principles

These principles apply to the **final application**, not this mockup:

* Local-first (data stored on device)
* Privacy-focused (no cloud required)
* Event-driven (no continuous monitoring)
* Minimal cognitive load (calm UI)

---

## 🔗 Related Documentation

* App (future implementation) → `../README.md`
* Device documentation → `../../device/`
* Roadmap → `../../docs/roadmap.md`
* Progress → `../../docs/progress.md`

---

## 📌 Notes

This prototype is a **design artifact**.

Its structure and behavior may change or be discarded as the real application evolves.
