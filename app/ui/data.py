# ui/data.py — Sensor registry, event log and formatters for the dashboard.
#
# Mirrors "Awareness Companion/src/lib/awareness-data.ts" so the Kivy UI
# stays aligned with the web design (same sensors, scales and thresholds).

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ui.theme import MAX_LOG_ENTRIES, RECENT_WINDOW_MIN, MINT, VIOLET, SKY


# ─────────────────────────────────────────────
# SENSOR REGISTRY — one entry per dashboard sensor
# ─────────────────────────────────────────────
@dataclass(frozen=True)
class Sensor:
    id: str
    label: str
    unit: str
    min: float
    max: float
    step: float
    default_threshold: float
    tone: str
    hint: str
    # Icon shown in the card tile (lucide-style spec key from ui/icons.py;
    # the design keeps icons in a separate ICONS map — merged here so the
    # Kivy card builder stays declarative).
    icon: str


SENSORS = [
    Sensor(
        id="light", label="Light", unit="lux", min=0, max=1200, step=20,
        default_threshold=800, tone="mint",
        hint="Alerts on bright or flickering environments", icon="light",
    ),
    Sensor(
        id="crowdness", label="Crowdness", unit="ppl/m²", min=0, max=6,
        step=0.1, default_threshold=3.5, tone="violet",
        hint="Alerts when the space around you gets dense", icon="crowdness",
    ),
    Sensor(
        id="noise", label="Noise", unit="dB", min=30, max=120, step=1,
        default_threshold=75, tone="sky",
        hint="Alerts on sustained loud sound", icon="noise",
    ),
]

TONE_COLORS = {"mint": MINT, "violet": VIOLET, "sky": SKY}
SENSOR_BY_ID = {s.id: s for s in SENSORS}
DEFAULT_THRESHOLDS = {s.id: s.default_threshold for s in SENSORS}

# Device light levels (0=dark, 1=normal, 2=bright) mapped to representative
# lux values so the design's lux scale stays meaningful with BLE data.
LIGHT_LEVEL_LUX = {0: 80, 1: 400, 2: 1000}

# Device sound levels (0=quiet, 1=normal, 2=loud) mapped to representative
# dB values on the noise scale; the default threshold (75 dB) then alerts
# on LOUD only, and sliding it lower adds NORMAL-level alerts.
NOISE_LEVEL_DB = {0: 45.0, 1: 70.0, 2: 95.0}

# Device crowd levels (0=low, 1=moderate, 2=high) mapped to representative
# ppl/m² values; the default threshold (3.5) then alerts on HIGH only.
CROWD_LEVEL_PPM = {0: 1.0, 1: 3.0, 2: 5.0}

# Traffic-light labels per level — what the device actually sends. Event
# rows show these words (not the representative units, which are a
# display scale, not a measurement).
LEVEL_LABELS = {
    "noise": {0: "QUIET", 1: "NORMAL", 2: "LOUD"},
    "light": {0: "DARK", 1: "NORMAL", 2: "BRIGHT"},
    "crowdness": {0: "LOW", 1: "MODERATE", 2: "HIGH"},
}
# Reverse map: representative scale value -> traffic-light label
VALUE_TO_LABEL = {
    "noise": {NOISE_LEVEL_DB[level]: LEVEL_LABELS["noise"][level]
              for level in LEVEL_LABELS["noise"]},
    "light": {LIGHT_LEVEL_LUX[level]: LEVEL_LABELS["light"][level]
              for level in LEVEL_LABELS["light"]},
    "crowdness": {CROWD_LEVEL_PPM[level]: LEVEL_LABELS["crowdness"][level]
                  for level in LEVEL_LABELS["crowdness"]},
}


def format_event_value(sensor_id, value):
    """Label for a logged event value: traffic-light word for noise/light
    (the device sends the label, not a measured unit), units otherwise."""
    label = VALUE_TO_LABEL.get(sensor_id, {}).get(value)
    if label is not None:
        return label
    return format_value(sensor_id, value)


# ─────────────────────────────────────────────
# FORMATTING HELPERS
# ─────────────────────────────────────────────
def format_value(sensor_id, value):
    """Format a raw value with its unit, e.g. 3.5 → '3.5 ppl/m²'."""
    s = SENSOR_BY_ID[sensor_id]
    return f"{value:g} {s.unit}"


def format_when(at):
    """Relative time label, e.g. '12 min ago', '3 h ago', 'Tue, 12 Aug'."""
    mins = int((datetime.now() - at).total_seconds() // 60)
    if mins < 60:
        return f"{max(mins, 1)} min ago"
    if mins < 60 * 24:
        return f"{mins // 60} h ago"
    return at.strftime("%a, %d %b")


def format_exact(at):
    """Full timestamp label, e.g. 'Mon, 12 Aug · 14:05'."""
    return at.strftime("%a, %d %b · %H:%M")


# ─────────────────────────────────────────────
# EVENT LOG
# ─────────────────────────────────────────────
@dataclass
class AwarenessEvent:
    sensor: str
    value: float
    threshold: float
    at: datetime = field(default_factory=datetime.now)


class EventsStore:
    """In-memory log of threshold-crossing alerts, newest first."""

    def __init__(self, max_entries=MAX_LOG_ENTRIES):
        self._entries = []
        self._max = max_entries

    def add(self, sensor, value, threshold, at=None):
        """Append an event; the oldest entry is dropped past the cap."""
        self._entries.append(
            AwarenessEvent(sensor, value, threshold, at or datetime.now())
        )
        if len(self._entries) > self._max:
            self._entries.pop(0)

    def all(self):
        """All events, newest first."""
        return list(reversed(self._entries))

    def clear(self):
        """Drop every logged event — used when the first real device
        connection replaces the seeded demo alerts."""
        self._entries = []

    def recent(self, limit):
        """The `limit` newest events, newest first."""
        return self.all()[:limit]

    def last_for(self, sensor_id):
        """The newest event for one sensor, or None."""
        for e in reversed(self._entries):
            if e.sensor == sensor_id:
                return e
        return None

    def last_event_seconds_ago(self, sensor_id):
        """Seconds since the newest event for one sensor (None if none)."""
        e = self.last_for(sensor_id)
        if e is None:
            return None
        return (datetime.now() - e.at).total_seconds()

    def is_recent_alert(self, sensor_id):
        """True when the sensor reported an alert within the last
        RECENT_WINDOW_MIN minutes. Deliberately independent of the current
        threshold: an alert that happened stays "recent" for the window
        even if the user later raises the threshold."""
        e = self.last_for(sensor_id)
        if e is None:
            return False
        age = datetime.now() - e.at
        return age.total_seconds() < RECENT_WINDOW_MIN * 60

    def seed_demo(self):
        """Demo alerts matching the design reference so the dashboard reads
        like the Awareness Companion screenshots on first launch."""
        # (sensor, value, threshold, minutes ago)
        demo = [
            ("noise", 88, 75, 12),
            ("crowdness", 4.1, 3.5, 74),
            ("light", 940, 800, 180),
            ("noise", 79, 75, 320),
            ("crowdness", 5.2, 3.5, 1_200),
            ("light", 1010, 800, 1_640),
            ("noise", 92, 75, 2_500),
            ("crowdness", 3.9, 3.5, 3_100),
            ("light", 860, 800, 4_400),
            ("noise", 81, 75, 5_800),
            ("crowdness", 4.6, 3.5, 7_100),
            ("light", 1120, 800, 8_900),
        ]
        now = datetime.now()
        for sensor, value, threshold, mins in demo:
            self.add(sensor, value, threshold, now - timedelta(minutes=mins))
