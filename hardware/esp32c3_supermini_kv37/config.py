# ═══════════════════════════════════════════
# ADC PINS — ESP32-C3
# ═══════════════════════════════════════════
MIC_GPIO       = 0       # ADC1_CH0 for analog mic
LIGHT_GPIO     = 1       # ADC1_CH1 for LDR
BAT_GPIO_PIN   = 3       # ADC1_CH3 to devide tension

# ═══════════════════════════════════════════
# SOUND — ADC Bit Range Limits
# ═══════════════════════════════════════════
ADC_MIN_BIT = 0         # min abs value - equivalent to 0 V
ADC_MAX_BIT = 65535     # max abs value - equivalente to 3.3V in 16bits scale

# ═══════════════════════════════════════════
# SOUND — traffic light
# ═══════════════════════════════════════════
SOUND_QUIET    = 15000   # diff < QUIET   
SOUND_MODERATE = 38000   # diff < MODERATE
# diff >= MODERATE       → LOUD (alert)
SAMPLE_TIME    = 0.05    # 50ms samples from ADC (~20 Hz)
SOUND_COOLDOWN = 2.0     # min seconds between same level notifications to BLE

# ═══════════════════════════════════════════
# LIGHT — traffic light 3 levels (LDR + resistence)
# ═══════════════════════════════════════════
LIGHT_DARK     = 15500   # raw < DARK
LIGHT_MODERATE = 18000   # raw < MODERATE
# raw >= MODERATE        → BRIGHT
LIGHT_SAMPLE   = 1.0     # sec between samples (slow sensor, save CPU)
LIGHT_COOLDOWN = 3.0     # min sec between same level notifications to BLE

# ═══════════════════════════════════════════
# CROWDNESS — Wi-Fi Traffic Light [NUEVO]
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
BAT_GPIO       = 3       # GPIO of the voltage divider towards the positive LiPo (ADC1_CH2 on ESP32-C5)
BAT_INTERVAL   = 30.0    # between reads
BAT_VMAX       = 4.2     # voltage LiPo (100% - fully charged)
BAT_VMIN       = 3.0     # voltage LiPo (0%- safety cut)
BAT_DIVIDER    = 2.0     # factor del divisor R1=R2 → Vbat = Vadc × 2
BAT_REF        = 3.3     # reference tensionfrom ADC in ESP32-C5
BAT_WARN_PCT   = 20      # % under which it is marked as "needs charging"

# ═══════════════════════════════════════════
# BLE
# ═══════════════════════════════════════════
ADV_INTERVAL_US = 500_000   # 500ms advertising (vs 100ms original → ~5× menos radio)
