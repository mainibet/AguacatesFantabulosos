# ui/theme.py — matched to HTML prototype dark mode

BG        = (0.059, 0.067, 0.082, 1)   # #0f1115
CARD      = (0.090, 0.102, 0.129, 1)   # #171a21
TEXT      = (0.949, 0.949, 0.949, 1)   # #f2f2f2
MUTED     = (1, 1, 1, 0.6)
ACCENT    = (0.357, 0.549, 1.0,   1)   # #5b8cff
BAR_BG    = (0.110, 0.125, 0.161, 1)   # #1c2029
THRESHOLD = (1, 1, 1, 0.85)
BORDER    = (0.165, 0.188, 0.227, 1)   # #2a2f3a

# Log events: same as app background, grey border
ALERT_BG     = (0.059, 0.067, 0.082, 1)   # same as BG #0f1115
ALERT_BORDER = (0.22,  0.25,  0.30,  1)

# Audio
DB_MIN   = 40.0
DB_MAX   = 100.0
CHUNK    = 1024
RATE     = 44100
CHANNELS = 1

# UI
WINDOW_SIZE     = (420, 780)
POLL_INTERVAL   = 0.15
MAX_LOG_ENTRIES = 6