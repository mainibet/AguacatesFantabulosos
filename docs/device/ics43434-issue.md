# ICS-43434 microphone — issue report & test guide

**Status: microphone part suspected defective — needs hardware verification by the next tester.**

## Context

The wearable's sound sensor has two variants in the repo:

| Variant | Mic | Path | Location |
|---|---|---|---|
| KV-37 | Analog electret (KY-037) | ADC (GPIO 0) | `hardware/esp32c3_supermini_kv37/` |
| **ICS-43434** | Digital MEMS (I2S) | **I2S** (SCK→5, WS→4, SD→6) | `hardware/esp32c3_supermin_ics43434/` |

The ICS-43434 firmware is **fully adapted for I2S** (not ADC): `machine.I2S` RX,
32-bit stereo @ 16 kHz, L/R slot selection, 24-bit sample extraction, I2S-based
calibration, and the same BLE traffic-light + threshold-sync logic as the KV-37
variant. It boots cleanly — but the mic produces **no data at all**.

## Wiring (verified)

| ICS-43434 pin | ESP32-C3 Super Mini pin |
|---|---|
| VDD | 3V3 (measured 3.3 V ✓) |
| GND | GND (shared ✓) |
| SCK (BCLK) | GPIO 5 |
| WS (LRCK) | GPIO 4 |
| SD (DATA/DOUT) | GPIO 6 |
| L/R | GND (LEFT channel, slot offset 0) |

Config matches this wiring (`MIC_SCK_GPIO=5, MIC_WS_GPIO=4, MIC_SD_GPIO=6,
MIC_SLOT="L"`). Note: the config values were previously wrong (SD=10, slot R)
and were corrected to match the documented wiring.

## Diagnosis

### What works (verified by tests)

1. **Firmware boots**: `Calibrating ... → Baseline amplitude: 0 → Waiting for connection...`
2. **BLE works**: the full traffic-light + threshold-sync contract runs on this
   firmware (verified against the app on the KV-37 variant).
3. **I2S clocks**: WS toggles; **BCLK toggles after reflashing MicroPython** (see below).

### Defect found in MicroPython v1.28.0 (fixed by reflash)

The board originally ran MicroPython **v1.28.0 (2026-04-06)**. On this build,
`machine.I2S` on the ESP32-C3 generates the **WS clock but never the BCLK** —
a GPIO scan during I2S RX showed only GPIO4 (WS) toggling; BCLK was absent on
every pin, at every rate (8/16/48 kHz), format (STEREO/MONO) and bit depth
(16/32). Without BCLK the mic cannot clock data out, so I2S reads returned
pure zeros regardless of wiring or pins.

**Action taken**: erased flash and reflashed **MicroPython v1.26.1**
(`ESP32_GENERIC_C3-20250911-v1.26.1.bin`, flashed with `esptool.py write_flash
0 <bin>`). After re-uploading `boot.py`, `lib/aioble`, `main.py`, `config.py`,
both BCLK and WS toggle (verified by GPIO sampling). The v1.28.0 build is a
known-bad I2S build for the ESP32-C3; keep the board on v1.26.1.

### Remaining problem: the microphone outputs nothing

With v1.26.1 (clocks working) and the verified wiring, all I2S reads are still
zero:

- **Both stereo slots** read `amp 0` across multiple 50 ms buffers.
- **All SD pin candidates** (GPIO 2/6/7/10) and **all clock combos**
  (SCK/WS swapped) read zero.
- **All-GPIO scan** while I2S runs: only the clock pins toggle — no data
  signal anywhere.
- **SD line floats**: GPIO6 read with internal pull-up during I2S stays HIGH.
  A powered, clocked ICS-43434 drives SD **low** when idle — floating SD means
  the mic's output is not reaching the pin (dead part or open connection).

### Cross-board confirmation (reported by the owner)

The same silence was observed with the mic connected to a **second ESP32-C3
Super Mini** and an **ESP32-C5**, with **new wires and a different breadboard**.
VDD was measured at the mic at 3.3 V.

## Conclusion

Wiring, configuration, and firmware are eliminated as causes. The remaining
suspect is **the microphone itself**: defective, or not a genuine ICS-43434
(mislabeled/lookalike part with a different pinout). The ICS-43434 has no
enable pin — given VDD + clocks + L/R strap, it must start outputting data on
SD within ~1 ms of power-up.

## What the next tester should do

1. **Verify the part** — check the printed marking on the mic (should be
   ICS-43434 / 43434; lookalikes exist). Confirm the pin order of the actual
   package against its datasheet (VDD, GND, SD, WS, SCK, L/R — order varies
   between clones).
2. **Replace the mic** with a known-good ICS-43434 (or a verified equivalent
   such as INMP441 / SPH0645 with adjusted slot config), then rerun the probe
   below. Expected: `Baseline amplitude` **> 0** at boot, and SD drives low.
3. **If a new mic still reads zero**, re-verify the SD wire with a continuity
   check (the breadboard contact can look seated but not connect), then rerun
   the probe.

### Quick verification probe (board on MicroPython v1.26.1)

```python
# mpremote exec, with main.py parked (rename to main.bak) for a clean I2S
import config
from machine import Pin, I2S
import struct, time
a = I2S(0, sck=Pin(config.MIC_SCK_GPIO), ws=Pin(config.MIC_WS_GPIO),
        sd=Pin(config.MIC_SD_GPIO), mode=I2S.RX, bits=config.MIC_BITS,
        format=I2S.STEREO, rate=config.MIC_SAMPLE_RATE, ibuf=16384)
time.sleep(0.5)
buf = bytearray(config.MIC_BUF_BYTES)
n = a.readinto(buf)
for off in (0, 4):
    mx, mn = -0x80000000, 0x7FFFFFFF
    for i in range(0, n - 3, 8):
        v = struct.unpack_from('<i', buf, i + off)[0] >> 8
        mx, mn = max(mx, v), min(mn, v)
    print('slot', off, 'amp', mx - mn)     # working mic: amp > 0 on the mic slot
a.deinit()
```

SD-connection check (0 = mic driving the line, 1 = floating/open):

```python
from machine import Pin
p = Pin(6, Pin.IN, Pin.PULL_UP)
print('SD state (0=driven, 1=floating):', p.value())
```

## Useful files

- `hardware/esp32c3_supermin_ics43434/main.py` — I2S + BLE firmware
- `hardware/esp32c3_supermin_ics43434/config.py` — pins/thresholds (already corrected)
- `hardware/esp32c3_supermini_kv37/` — analog mic variant (known working; revert the board to it with `mpremote cp` if the digital mic stays unavailable)
