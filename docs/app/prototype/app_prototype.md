# Awareness App

## 📌 Overview

The Awareness App is a desktop/mobile application designed to receive, display, and manage **event-based environmental alerts** from a wearable device.

The system is **event-driven**, meaning it does not continuously stream sensor data.
Instead, it reacts only when predefined thresholds are exceeded.

The app is built with a **local-first approach**, ensuring privacy and offline usability.

---

## 🎯 Purpose

* Provide real-time awareness of environmental conditions
* Reduce cognitive overload through minimal, meaningful alerts
* Store and explore event data locally

---

## ⚙️ Current Scope (v0.1)

This is the initial version of the app, focused on simplicity:

* Receive **noise alerts** from the device
* Display alert notifications
* Store a basic **event log locally**
* No configuration or device control yet

---

## 🚀 Planned Features

### 📡 Device Communication

* Bluetooth (BLE) connection with the wearable device
* Reliable event transmission

### 🎛️ Configuration

* Set threshold values per sensor from the app
* Sync configuration with the device

### 🌡️ Multi-Sensor Support

* Noise
* Light
* Crowd density

### 📊 Data Visualization

* Event timeline
* Frequency graphs
* Pattern exploration (future)

### 💾 Data Management

* Local database (SQLite)
* Event history and filtering

---

## 📡 Communication Model

The system follows an **event-based architecture**:

* Device → App

  * Sends alerts only when thresholds are exceeded

* App → Device *(planned)*

  * Sends configuration (thresholds, settings) via BLE

---

## 🧠 Data Model (Conceptual)

Each event contains:

* Timestamp
* Sensor type (noise, light, crowd)
* Intensity level

All data is stored locally on the user’s device.

---

## 🧪 Usage

*(To be defined as implementation progresses)*

For now, see the prototype:

👉 `./prototype/`

---

## 🧠 Design Principles

* **Local-first** → no cloud dependency
* **Privacy-focused** → user data stays on device
* **Event-driven** → no continuous monitoring
* **Minimal cognitive load** → calm, non-intrusive UI

---

## 🔄 Relationship with Prototype

A UI prototype exists for design validation:

👉 `./prototype/`

The prototype:

* Simulates behavior
* Does not reflect final architecture
* May diverge significantly from the final implementation

---

## 🔗 Related Documentation

* Device → `../device/`
* Roadmap → `../docs/roadmap.md`
* Progress → `../docs/progress.md`
* Changelog → `../CHANGELOG/app.md`

---

## 📌 Status

Active development — evolving through incremental versions.
