# ui/theme.py — Colors and visual constants
 
# Dark theme palette
BG        = (0.059, 0.067, 0.082, 1)   # #0f1115
CARD      = (0.090, 0.102, 0.129, 1)   # #171a21
ACCENT    = (0.357, 0.549, 1.0,   1)   # #5b8cff
BAR_BG    = (0.110, 0.125, 0.161, 1)   # #1c2029
TEXT      = (0.949, 0.949, 0.949, 1)   # #f2f2f2
MUTED     = (1, 1, 1, 0.5)
BORDER    = (0.165, 0.188, 0.227, 1)   # #2a2f3a
THRESHOLD = (1, 1, 1, 0.85)
ALERT_BG  = (0.2, 0.1, 0.1, 1)
 
# Audio range (dB)
DB_MIN = 40.0
DB_MAX = 100.0
 
# Audio capture settings
CHUNK    = 1024
RATE     = 44100
CHANNELS = 1
 
# UI
WINDOW_SIZE      = (420, 780)
POLL_INTERVAL    = 0.15    # seconds between UI updates (~7 fps)
MAX_LOG_ENTRIES  = 6
 