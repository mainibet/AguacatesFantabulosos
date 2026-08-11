# ICS-43434 Lab Diagnostic — ESP32-C3

## Problem (short)
The ICS-43434 (I2S digital mic, WS→GPIO4, SCK→GPIO5, SD→GPIO10, L/R→3V3) produces no audio. Every `I2S.readinto()` returns constant `0xFFFFFFFF` (all words = `-1`) or `0x00000000` on every SD pin tested, at 8–48 kHz, MONO/STEREO, all SCK/WS permutations. Music playing near the mic changes nothing.

## Options tested
- Pin permutations SCK/WS/SD, sample rates 8k–48k, MONO/STEREO → all constant output.
- GPIO9 → boot strapping pin with external pull-up, unusable.
- **What turned out OK**: I2S clock runs at exactly 128,000 B/s (correct for 16 kHz stereo 32-bit); clocks toggle on GPIO4/5; RX path proven working — driving SD manually yields 73–82 distinct values. One capture on GPIO6 after re-wiring showed real 24-bit audio (min −2,021,489 / max +6,705,470) before going silent again.

## Diagnosis (potential issue)
SD pin is electrically **floating** — internal pull resistors flip the reading (PULL_DOWN→zeros, PULL_UP→`-1`), so the mic's push-pull SD output is not reaching the GPIO. 

Most likely: intermittent/broken SD jumper contact, missing VDD to the mic, or missing ≥1 µF decoupling cap on VDD (required by the ICS-43434 datasheet; without it the mic fails to start).

## Checklist (power off first)
- [ ] Multimeter at the **mic's VDD pin** vs GND → must read ~3.3 V.
- [ ] Add ≥1 µF capacitor between VDD and GND, as close to the mic as possible.
- [ ] Continuity check: SD↔GPIO10, SCK↔GPIO5, WS↔GPIO4, VDD→3V3, GND→GND, L/R→3V3.
- [ ] Power on, run `mpremote connect <port> run probe_i2s.py` (in this folder).
- [ ] Pass = amplitude > 0 in capture step AND pull test doesn't change the reading. Then flash `config.py` + `main.py` and calibrate thresholds.

## How was verified
Live over serial with `mpremote`: probed `GPIO_IN` register (clocks toggle), timed `readinto` (128,000 B/s), drove SD pins manually (RX path captures distinct values), and pull-tested each candidate pin (floating pin follows pulls; a driven push-pull output ignores them).
