# ═══════════════════════════════════════════
# SOUND — traffic light
# ═══════════════════════════════════════════
SOUND_QUIET    = 500     # diff < QUIET   
SOUND_MODERATE = 2000    # diff < MODERATE
# diff >= MODERATE       → LOUD (alert)

SAMPLE_TIME    = 0.05    # 50ms samples from ADC (~20 Hz)
SOUND_COOLDOWN = 2.0     # min seconds between same level notifications to BLE

# ═══════════════════════════════════════════
# LIGHT — traffic light 3 levels (LDR + resistence)
# ═══════════════════════════════════════════
LIGHT_DARK     = 10000   # raw < DARK
LIGHT_MODERATE = 40000   # raw < MODERATE
# raw >= MODERATE        → BRIGHT

LIGHT_SAMPLE   = 1.0     # sec between samples (slow sensor, save CPU)
LIGHT_COOLDOWN = 3.0     # min sec between same level notifications to BLE

# ═══════════════════════════════════════════
# BATTERY
# ═══════════════════════════════════════════
BAT_GPIO       = 3       # GPIO of the voltage divider towards the positive LiPo
BAT_INTERVAL   = 30.0    # between reads
BAT_VMAX       = 4.2     # voltage LiPo (100% - fully charged)
BAT_VMIN       = 3.0     # voltage LiPo (0%- safety cut)
BAT_DIVIDER    = 2.0     # factor del divisor R1=R2 → Vbat = Vadc × 2
BAT_REF        = 3.3     # tensión de referencia del ADC del ESP32-C3
BAT_WARN_PCT   = 20      # % under which it is marked as "needs charging"

# ═══════════════════════════════════════════
# BLE
# ═══════════════════════════════════════════
ADV_INTERVAL_US = 500_000   # 500ms advertising (vs 100ms original → ~5× menos radio)