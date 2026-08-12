# ═══════════════════════════════════════════
# I2S PINS — ESP32-C3 + ICS-43434 (digital MEMS mic)
# ═══════════════════════════════════════════
# ICS-43434 wiring:
#   VDD → 3V3, GND → GND, L/R → GND (LEFT channel)
#   WS (LRCK) → GPIO4, SCK (BCLK) → GPIO5, SD (DATA) → GPIO6
MIC_SCK_GPIO  = 5       # BCLK — bit clock from ESP32 to mic
MIC_WS_GPIO   = 4       # LRCK — word select from ESP32 to mic
MIC_SD_GPIO   = 6       # DATA — audio samples from mic to ESP32
MIC_SLOT      = "L"     # L/R → GND selects LEFT channel (offset 0); use "R" if L/R → 3V3

# ═══════════════════════════════════════════
# SOUND — I2S sampling
# ═══════════════════════════════════════════
MIC_SAMPLE_RATE = 16000 # Hz (ICS-43434 supports 16–50 kHz)
MIC_BITS        = 32    # container size; 24-bit mic data is left-justified
MIC_BUF_BYTES   = 3200  # 50 ms window @16 kHz stereo 32-bit (800 samples × 4B)
SOUND_COOLDOWN  = 2.0   # min seconds between same level notifications to BLE

# ═══════════════════════════════════════════
# SOUND — traffic light (amplitude = peak-to-peak of 24-bit samples)
# ═══════════════════════════════════════════
# NOTE: thresholds below are PLACEHOLDERS — the ICS-43434 outputs 24-bit
# samples (±8.4M full scale), a completely different scale from the old
# KY-037 16-bit ADC. Recalibrate with real measurements once the mic works.
SOUND_QUIET    = 500_000   # amplitude < QUIET
SOUND_MODERATE = 2_000_000 # amplitude < MODERATE
# amplitude >= MODERATE    → LOUD (alert)

# ═══════════════════════════════════════════
# LIGHT — ADC pins (LDR) & traffic light
# ═══════════════════════════════════════════
LIGHT_GPIO     = 1       # ADC1_CH1 for LDR
LIGHT_DARK     = 15500   # raw < DARK
LIGHT_MODERATE = 18000   # raw < MODERATE
# raw >= MODERATE        → BRIGHT
LIGHT_SAMPLE   = 1.0     # sec between samples (slow sensor, save CPU)
LIGHT_COOLDOWN = 3.0     # min sec between same level notifications to BLE

# ═══════════════════════════════════════════
# CROWDNESS — Wi-Fi Traffic Light
# ═══════════════════════════════════════════
CROWD_LOW        = 5     # < 5 unique devices → LOW
CROWD_MODERATE   = 15    # < 15 unique devices → MODERATE
# >= 15                  → HIGH (alert)
CROWD_WINDOW_SEC = 30    # Accumulation window (sec)
CROWD_COOLDOWN   = 5.0   # Sec mini between notifications
RSSI_THRESHOLD   = -80   # Power threshold in dBm for far filtering

# ═══════════════════════════════════════════
# BATTERY
# ═══════════════════════════════════════════
BAT_GPIO_PIN   = 3       # ADC1_CH3 to divide tension
BAT_INTERVAL   = 30.0    # between reads
BAT_VMAX       = 4.2     # voltage LiPo (100% - fully charged)
BAT_VMIN       = 3.0     # voltage LiPo (0%- safety cut)
BAT_DIVIDER    = 2.0     # factor del divisor R1=R2 → Vbat = Vadc × 2
BAT_REF        = 3.3     # reference tension from ADC in ESP32-C3
BAT_WARN_PCT   = 20      # % under which it is marked as "needs charging"

# ═══════════════════════════════════════════
# APP THRESHOLDS — event-driven alerts (set from the app)
# The device only notifies over BLE when the app-set threshold is
# exceeded; the app pushes updates via the config characteristic.
# ═══════════════════════════════════════════
NOISE_THRESHOLD = 75.0    # dB (representative scale; default matches the app)
LIGHT_THRESHOLD = 800.0   # lux (representative scale; default matches the app)

# Traffic-light level → representative scale value (same mapping as the app,
# so device-side gating agrees with the app's threshold slider)
NOISE_LEVEL_DB  = {"QUIET": 45.0, "NORMAL": 70.0, "LOUD": 95.0}
LIGHT_LEVEL_LUX = {"DARK": 80.0, "NORMAL": 400.0, "BRIGHT": 1000.0}

# ═══════════════════════════════════════════
# BLE
# ═══════════════════════════════════════════
ADV_INTERVAL_US = 500_000   # 500ms advertising (vs 100ms original → ~5× less radio)
