# ui/theme.py — Design tokens for the Awareness Companion dashboard.
#
# The palette is converted from the Awareness Companion web design
# (oklch values in "Awareness Companion/src/styles.css") to sRGB so the
# Kivy app matches the reference UI. Keep every color, size and constant
# of the design system in this single module.

# ─────────────────────────────────────────────
# COLOR PALETTE — dark indigo design system
# ─────────────────────────────────────────────
BG          = (0.110, 0.106, 0.250, 1)   # page background
CARD        = (0.154, 0.153, 0.319, 1)   # card / panel surface
SURFACE     = (0.183, 0.183, 0.369, 1)   # raised surface (pressed / hover)
TEXT        = (0.941, 0.934, 0.989, 1)   # primary text
MUTED       = (0.674, 0.667, 0.790, 1)   # secondary text
BORDER      = (0.242, 0.233, 0.420, 1)   # hairlines, rings and dividers
SECONDARY   = (0.192, 0.192, 0.386, 1)   # pill / button fill
PRIMARY     = (0.353, 0.259, 0.640, 1)   # primary accent
PRIMARY_FG  = (0.961, 0.955, 0.999, 1)

# Sensor tone accents + alert amber
MINT        = (0.207, 0.863, 0.636, 1)   # light sensor tone
VIOLET      = (0.560, 0.498, 0.839, 1)   # crowdness sensor tone
AMBER       = (1.000, 0.819, 0.399, 1)   # alert tone
SKY         = (0.478, 0.721, 0.960, 1)   # noise sensor tone


def alpha(color, a):
    """Return the color with a new alpha channel (0–1)."""
    return (color[0], color[1], color[2], a)


# ─────────────────────────────────────────────
# NOISE SCALE — matches the Noise sensor range in the design (30–120 dB)
# ─────────────────────────────────────────────
DB_MIN = 30.0
DB_MAX = 120.0


# ─────────────────────────────────────────────
# APP BEHAVIOUR
# ─────────────────────────────────────────────
WINDOW_SIZE       = (400, 700)     # desktop dev window (phone-shaped)
POLL_INTERVAL     = 0.15           # seconds between UI refreshes
MAX_LOG_ENTRIES   = 200            # event store cap
RECENT_WINDOW_MIN = 5             # "Recent alert" pill window (minutes)

# ─────────────────────────────────────────────
# RADII AND TYPOGRAPHY — tweak sizes here only
# ─────────────────────────────────────────────
RADIUS_CARD = 24                   # rounded-3xl (cards, panels)
RADIUS_TILE = 16                   # rounded-2xl (sensor icon tiles)
RADIUS_ROW  = 12                   # rounded-xl (event row icon tiles)

FONT_EYEBROW = '12sp'              # section eyebrow (AWARENESS, SENSORS)
FONT_TITLE   = '28sp'              # page title (Wearable)
FONT_LABEL   = '16sp'              # sensor names
FONT_BODY    = '14sp'              # body copy
FONT_CAPTION = '12sp'              # captions, pills, meta text
