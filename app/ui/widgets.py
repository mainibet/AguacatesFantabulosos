    # ui/widgets.py — Custom Kivy widgets
 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from datetime import datetime
 
from ui.theme import (
    CARD, BORDER, ACCENT, BAR_BG, THRESHOLD,
    TEXT, MUTED, ALERT_BG, DB_MIN, DB_MAX, MAX_LOG_ENTRIES
)
 
 
def _pct(value):
    """Normalize a dB value to 0-1 within DB_MIN..DB_MAX range."""
    return (value - DB_MIN) / (DB_MAX - DB_MIN)
 
 
class Card(BoxLayout):
    """BoxLayout with rounded card background."""
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(18)
        self.spacing = dp(8)
        with self.canvas.before:
            Color(*CARD)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            Color(*BORDER)
            self._border = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(pos=self._update, size=self._update)
 
    def _update(self, *_):
        self._rect.pos    = self.pos
        self._rect.size   = self.size
        self._border.pos  = self.pos
        self._border.size = self.size
 
 
class NoiseBar(Widget):
    """Animated dB level bar with a threshold marker line."""
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(22)
        self._fill_pct      = 0.0
        self._threshold_pct = _pct(75)
        self._draw()
        self.bind(pos=self._redraw, size=self._redraw)
 
    def update(self, db_value, threshold):
        """Call this every tick with the current dB and threshold values."""
        self._fill_pct      = _pct(db_value)
        self._threshold_pct = _pct(threshold)
        self._redraw()
 
    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            # Background track
            Color(*BAR_BG)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            # Level fill
            fill_w = self.width * self._fill_pct
            Color(*ACCENT)
            RoundedRectangle(
                pos=self.pos,
                size=(max(fill_w, dp(4)), self.height),
                radius=[dp(10)]
            )
            # Threshold marker
            tx = self.x + self.width * self._threshold_pct
            Color(*THRESHOLD)
            Rectangle(pos=(tx - dp(1), self.y), size=(dp(2), self.height))
 
    def _redraw(self, *_):
        self._draw()
 
 
class LogList(BoxLayout):
    """Vertical list of alert events, newest first, capped at MAX_LOG_ENTRIES."""
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing     = dp(6)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self._items = []
 
    def add_event(self, db_value):
        """Add a new alert entry to the top of the log."""
        t    = datetime.now().strftime("%H:%M:%S")
        text = f"[!] {t}  —  {db_value:.0f} dB exceeded threshold"
 
        lbl = Label(
            text=text,
            font_size='13sp',
            color=TEXT,
            size_hint_y=None,
            height=dp(40),
            text_size=(Window.width - dp(50), None),
            halign='left',
            valign='middle',
        )
        with lbl.canvas.before:
            Color(*ALERT_BG)
            RoundedRectangle(pos=lbl.pos, size=lbl.size, radius=[dp(10)])
        lbl.bind(pos=lambda w, v: setattr(w.canvas.before.children[1], 'pos', v))
        lbl.bind(size=lambda w, v: setattr(w.canvas.before.children[1], 'size', v))
 
        self._items.insert(0, lbl)
        if len(self._items) > MAX_LOG_ENTRIES:
            self._items.pop()
 
        self.clear_widgets()
        for item in self._items:
            self.add_widget(item)