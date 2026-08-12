
### v0.4.0 - App-threshold gating & traffic-light notifications (current)
- **Traffic-light notifications**: sound now sends its status for every level (`SOUND:LOUD|Red|noise=…`, consistent with light and crowd) instead of only `ALERT:LOUD` with a raw amplitude.
- **Config characteristic** (`…4325`, writable): the device receives the app's thresholds (`noise=…;light=…`) and gates its notifications on them; the firmware defaults (75 / 800) are the fallback until the app pushes.
- **Edge re-arm on threshold change**: lowering the threshold while a level is already above re-notifies (previously the detector stayed latched).
- **Crowd initial reading**: the crowd monitor sends its first reading immediately on connect instead of after the 30 s accumulation window.
- **aioble `capture=True`** on the config characteristic: `written()` otherwise returns the connection object instead of the payload, breaking the threshold parse.
- **MicroPython v1.28.0 I2S defect**: on the ESP32-C3, `machine.I2S` on v1.28.0 never outputs BCLK (WS only), so digital MEMS mics (ICS-43434) receive no bit clock and produce no data. Reflashed the board to **v1.26.1**, where BCLK/WS both toggle (verified by GPIO sampling).
- **ICS-43434 status**: I2S path adapted (SCK→5, WS→4, SD→6, L/R→GND) and config corrected to match; SD line reads floating even with VDD and clocks present — the mic part itself is suspect (defective or non-genuine), confirmed silent across two other boards.
- **Hardware notes**: battery divider reads `BAT:0%|V:1.75` while charging (calibration pending — below the 3.0 V floor); this MicroPython build lacks `esp32.raw_dot11_sniffer`, so crowd always reports 0 devices; the board can hang after a deep power loss until replug/reset.

### v0.3.0 - Connection hardening
- **Crowdness**: Guarded `esp32.raw_dot11_sniffer` behind a capability check — builds without the sniffer API no longer crash the BLE session (report 0 instead).
- **BLE lifecycle**: Monitor tasks are now guarded and cancelled on disconnect — a failing monitor can no longer tear down the connection, and no zombie tasks keep spamming errors against a dead connection after the client leaves.
- **Reconnect**: Verified the device re-advertises after every disconnect (loop was previously unreachable when the monitors stayed alive).

### v0.2.1 - Battery & Light Sensor
- **Battery**: Voltage-divider ADC (GPIO 3) reads the LiPo voltage, converts it to a percentage (Vmax 4.2 V / Vmin 3.0 V), and sends `BAT:xx%|V:x.xx` over BLE (averaged reads, notify only when the % changes, 30 s interval).
- **Light**: LDR on GPIO 1 classified into a 3-level traffic light (DARK / MODERATE / BRIGHT), sent as `LIGHT:status|color|RAW:value` over BLE with a cooldown between same-level notifications.

### v0.2.0 - Bluetooth Low Energy Integration
- **Firmware**: Migrated from síncronous `while` loop to `asyncio` architecture.
- **Communication**: Implemented `aioble` for real-time alerting.
- **Sensor**: ESP32-C3 ADC integration for microphone (GPIO 0).
- **Calibration**: Added non-blocking asynchronous calibration at startup.

### v0.1.0 - Initial ADC Prototype
- Basic threshold detection using RP2040.