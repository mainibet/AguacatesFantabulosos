# ui/widgets.py

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.core.window import Window
from datetime import datetime
import numpy as np

from ui.theme import (
    CARD, BORDER, ACCENT, BAR_BG, THRESHOLD,
    TEXT, ALERT_BG, ALERT_BORDER, DB_MIN, DB_MAX, MAX_LOG_ENTRIES
)


def _pct(value):
    return max(0.0, min(1.0, (value - DB_MIN) / (DB_MAX - DB_MIN)))


_STRIPE_TEX = None

def _get_stripe_tex():
    global _STRIPE_TEX
    if _STRIPE_TEX is not None:
        return _STRIPE_TEX
    size = 24
    tex = Texture.create(size=(size, size), colorfmt='rgba')
    buf = np.zeros((size, size, 4), dtype=np.uint8)
    r, g, b = 91, 140, 255
    for i in range(size):
        for j in range(size):
            d = (i + j) % 12
            if d < 6:
                buf[i, j] = [min(255, int(r + (255-r)*0.18)),
                              min(255, int(g + (255-g)*0.18)),
                              min(255, int(b + (255-b)*0.18)), 255]
            else:
                buf[i, j] = [int(r*0.92), int(g*0.92), int(b*0.92), 255]
    tex.blit_buffer(buf.flatten().tobytes(), colorfmt='rgba', bufferfmt='ubyte')
    tex.wrap = 'repeat'
    _STRIPE_TEX = tex
    return tex


class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(18)
        self.spacing = dp(8)
        with self.canvas.before:
            Color(*CARD)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            Color(*BORDER)
            self._border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, dp(16)),
                width=1.1
            )
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._rect.pos  = self.pos
        self._rect.size = self.size
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(16))


class NoiseBar(Widget):
    """Level bar: 18px tall, rounded, diagonal stripes fill, white threshold marker."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(18)
        self._fill_pct      = 0.0
        self._threshold_pct = _pct(75)
        self.bind(pos=self._redraw, size=self._redraw)

    def update(self, db_value, threshold):
        self._fill_pct      = _pct(db_value)
        self._threshold_pct = _pct(threshold)
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        with self.canvas:
            # Background
            Color(*BAR_BG)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(9)])

            # Stripe fill — clipped by drawing only up to fill width
            fill_w = max(self.width * self._fill_pct, dp(4) if self._fill_pct > 0 else 0)
            if fill_w > 0:
                Color(1, 1, 1, 1)
                # Use stencil-free approach: draw rectangle with texture
                # rounded left edge only when fill doesn't reach end
                Rectangle(
                    texture=_get_stripe_tex(),
                    pos=self.pos,
                    size=(fill_w, self.height),
                )

            # Threshold marker
            tx = self.x + self.width * self._threshold_pct
            Color(*THRESHOLD)
            Rectangle(pos=(tx - dp(1), self.y), size=(dp(2), self.height))


class LogList(BoxLayout):
    """Alert event list — black bg, grey border, matching HTML .log-item."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing     = dp(8)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self._items = []

    def add_event(self, db_value):
        t    = datetime.now().strftime("%H:%M:%S")
        text = f"[!] {t}  —  {db_value:.0f} dB exceeded threshold"

        lbl = Label(
            text=text,
            font_size='14sp',
            color=TEXT,
            size_hint_y=None,
            height=dp(44),
            text_size=(Window.width - dp(68), None),
            halign='left',
            valign='middle',
        )

        with lbl.canvas.before:
            Color(*ALERT_BG)
            rect = RoundedRectangle(pos=lbl.pos, size=lbl.size, radius=[dp(10)])
            Color(*ALERT_BORDER)
            border_line = Line(
                rounded_rectangle=(lbl.x, lbl.y, lbl.width, lbl.height, dp(10)),
                width=1.1
            )

        def _upd(w, *_):
            rect.pos        = w.pos
            rect.size       = w.size
            border_line.rounded_rectangle = (w.x, w.y, w.width, w.height, dp(10))

        lbl.bind(pos=_upd, size=_upd)

        self._items.insert(0, lbl)
        if len(self._items) > MAX_LOG_ENTRIES:
            self._items.pop()

        self.clear_widgets()
        for item in self._items:
            self.add_widget(item)