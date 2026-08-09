# ui/icons.py — Line-drawn icons for the dashboard (lucide-style).
#
# Icons are defined on the lucide 24×24 grid and scaled to the widget size,
# so they stay crisp at any resolution. Each spec is a list of primitives:
#   ("line", x1, y1, x2, y2)           single segment
#   ("polyline", [x1, y1, x2, y2, ...]) connected path
#   ("circle", cx, cy, r)              circle outline
#   ("arc", cx, cy, r, a0, a1)         partial circle outline (degrees)

from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy.uix.widget import Widget


# ─────────────────────────────────────────────
# ICON DEFINITIONS — lucide 24×24 grid
# ─────────────────────────────────────────────
ICONS = {
    # Sun — circle plus eight rays (lucide "sun")
    "light": [
        ("circle", 12, 12, 4),
        ("line", 19, 12, 22, 12),
        ("line", 16.95, 16.95, 19.07, 19.07),
        ("line", 12, 19, 12, 22),
        ("line", 7.05, 16.95, 4.93, 19.07),
        ("line", 5, 12, 2, 12),
        ("line", 7.05, 7.05, 4.93, 4.93),
        ("line", 12, 5, 12, 2),
        ("line", 16.95, 7.05, 19.07, 4.93),
    ],
    # Users — two people, front and back (lucide "users")
    "crowdness": [
        ("circle", 9, 7, 4),
        ("arc", 10, 17.5, 6, 180, 360),
        ("circle", 17, 8, 3),
        ("arc", 18, 16, 4.5, 180, 360),
    ],
    # Audio lines — six vertical bars of varying height (lucide "audio-lines")
    "noise": [
        ("line", 2, 10, 2, 13),
        ("line", 6, 6, 6, 17),
        ("line", 10, 3, 10, 21),
        ("line", 14, 8, 14, 15),
        ("line", 18, 5, 18, 18),
        ("line", 22, 10, 22, 13),
    ],
    # History — clock face with hands and a rewind arrow (lucide "history")
    "history": [
        ("circle", 12, 12, 9),
        ("polyline", [3, 3, 3, 8, 8, 3]),
        ("polyline", [12, 7, 12, 12, 16, 14]),
    ],
    # Check (lucide "check")
    "check": [
        ("polyline", [20, 6, 9, 17, 4, 12]),
    ],
    # Triangle alert — outline plus exclamation (lucide "triangle-alert")
    "alert": [
        ("polyline", [12, 3, 22, 21, 2, 21, 12, 3]),
        ("line", 12, 10, 12, 16),
        ("line", 12, 18.6, 12, 19.4),
    ],
    # Close — two crossing segments (lucide "x")
    "close": [
        ("line", 6, 6, 18, 18),
        ("line", 18, 6, 6, 18),
    ],
    # Bluetooth — the classic five-segment symbol (lucide "bluetooth")
    "bluetooth": [
        ("polyline", [7, 7, 17, 17, 12, 22, 12, 2, 17, 7, 7, 17]),
    ],
}


# ─────────────────────────────────────────────
# ICON WIDGET — scales one spec into the widget box
# ─────────────────────────────────────────────
class IconWidget(Widget):
    """Renders one icon spec, scaled to the widget size and tinted.
    The drawing always stays centered inside the widget box, so the widget
    may be stretched on one axis without distorting the icon. Use
    set_color() to retint."""

    def __init__(self, name, color, size=(dp(16), dp(16)), **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self._spec = ICONS[name]
        with self.canvas:
            self._color_instr = Color(*color)
            # One Line instruction per segment/path/circle primitive
            self._paths = [
                Line(width=dp(1.3))
                for prim in self._spec if prim[0] != "dot"
            ]
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def set_color(self, color):
        self._color_instr.rgba = color

    def _draw(self, *_):
        w, h = self.width, self.height
        if w <= 0 or h <= 0:
            return
        # Scale the 24×24 grid to the widget box, keeping it centered
        scale = min(w, h) / 24.0
        ox = self.x + (w - 24 * scale) / 2
        oy = self.y + (h - 24 * scale) / 2

        def X(v):
            return ox + v * scale

        def Y(v):
            return oy + v * scale

        pi = 0
        for prim in self._spec:
            kind = prim[0]
            if kind == "line":
                _, x1, y1, x2, y2 = prim
                self._paths[pi].points = [X(x1), Y(y1), X(x2), Y(y2)]
                pi += 1
            elif kind == "polyline":
                coords = prim[1]
                self._paths[pi].points = [
                    X(v) if i % 2 == 0 else Y(v)
                    for i, v in enumerate(coords)
                ]
                pi += 1
            elif kind == "circle":
                _, cx, cy, r = prim
                self._paths[pi].circle = (X(cx), Y(cy), r * scale)
                pi += 1
            elif kind == "arc":
                _, cx, cy, r, a0, a1 = prim
                self._paths[pi].circle = (X(cx), Y(cy), r * scale, a0, a1)
                pi += 1
