# Roadmap

## Phase 1 — Noise detection (Mar 27 – Apr 30)
**Dates:** Apr 30

**Goal:** Working prototype with noise detection and real-time feedback

**Deliverable:** 
- ESP32 reads and processes noise levels
- Noise data transmitted via BLE
- Mobile app displays live noise level
- Basic alert triggered when threshold exceeded

## Phase 2 — Light (May 1 – May 31)
**Dates:** May 31

**Goal:** Integrate light detection and improve mobile app functionality

**Deliverable:** 
- Light sensor integrated and sending data  
- Mobile app displays both noise and light levels  
- Improved UI with clearer real-time feedback  
- First functional 3D-printed enclosure (v1) 

## Phase 3 — Crowd density detection (Jun 1 – Jun 20)
**Dates:** Jun 20

**Goal:** Add crowdedness estimation and improve the app with crowd-aware feedback

**Deliverable:** 
- ESP32 estimates whether the place is crowded or not, using nearby BLE/device signals or a density-based approach.

- Mobile app shows crowdedness status in real time, alongside noise and light data.

- Add sound feedback for crowdedness, with a distinct alert when the place becomes crowded.

- Second 3D-printed enclosure version (v2), refined after testing the first prototype.