# main.py — AwarenessApp entry point
 
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
 
from ui.theme import ACCENT, TEXT, MUTED, WINDOW_SIZE, POLL_INTERVAL
from ui.widgets import Card, NoiseBar, LogList
from services.audio import AudioMonitor
 
Window.clearcolor = (0.059, 0.067, 0.082, 1)
Window.size = WINDOW_SIZE
 
 
class RootLayout(BoxLayout):
 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding     = dp(16)
        self.spacing     = dp(16)
 
        self._threshold = 75.0
        self._monitor   = AudioMonitor()
        self._alerted   = False  # prevents log spam on sustained noise
 
        self._build_ui()
        self._monitor.start()
        Clock.schedule_interval(self._tick, POLL_INTERVAL)
 
    # ── UI assembly ───────────────────────────────────────────
 
    def _build_ui(self):
 
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(44))
        header.add_widget(Label(
            text="AwarenessApp",
            font_size='18sp', bold=True, color=TEXT,
            halign='left', valign='middle',
        ))
        header.add_widget(Label(
            text="● CONNECTED",
            font_size='12sp', color=ACCENT,
            size_hint_x=None, width=dp(120),
            halign='right',
        ))
        self.add_widget(header)
 
        # Level card
        level_card = Card(size_hint_y=None, height=dp(130))
        level_card.add_widget(Label(
            text="CURRENT NOISE LEVEL",
            font_size='13sp', bold=True, color=TEXT,
            size_hint_y=None, height=dp(24),
        ))
        self._status_lbl = Label(
            text="Monitoring environment...",
            font_size='12sp', color=MUTED,
            size_hint_y=None, height=dp(20),
        )
        level_card.add_widget(self._status_lbl)
        self._bar = NoiseBar()
        level_card.add_widget(self._bar)
        self._db_lbl = Label(
            text="-- dB",
            font_size='22sp', bold=True, color=ACCENT,
            size_hint_y=None, height=dp(36),
        )
        level_card.add_widget(self._db_lbl)
        self.add_widget(level_card)
 
        # Threshold card
        thresh_card = Card(size_hint_y=None, height=dp(110))
        thresh_card.add_widget(Label(
            text="THRESHOLD",
            font_size='13sp', bold=True, color=TEXT,
            size_hint_y=None, height=dp(24),
        ))
        self._thresh_lbl = Label(
            text="75 dB",
            font_size='14sp', color=ACCENT,
            size_hint_y=None, height=dp(22),
        )
        thresh_card.add_widget(self._thresh_lbl)
        slider = Slider(min=40, max=100, value=75, size_hint_y=None, height=dp(40))
        slider.bind(value=self._on_slider)
        thresh_card.add_widget(slider)
        self.add_widget(thresh_card)
 
        # Log section
        self.add_widget(Label(
            text="EVENT LOG",
            font_size='13sp', bold=True, color=TEXT,
            size_hint_y=None, height=dp(28),
            halign='left',
        ))
        scroll = ScrollView()
        self._log_list = LogList()
        scroll.add_widget(self._log_list)
        self.add_widget(scroll)
 
    # ── Callbacks ─────────────────────────────────────────────
 
    def _on_slider(self, slider, value):
        self._threshold       = value
        self._thresh_lbl.text = f"{value:.0f} dB"
 
    def _tick(self, dt):
        db = self._monitor.current_db
        self._db_lbl.text = f"{db:.1f} dB"
        self._bar.update(db, self._threshold)
 
        if db > self._threshold:
            if not self._alerted:
                self._log_list.add_event(db)
                self._alerted = True
        else:
            self._alerted = False
 
 
class AwarenessApp(App):
    def build(self):
        return RootLayout()
 
    def on_stop(self):
        self.root._monitor.stop()
 
 
if __name__ == "__main__":
    AwarenessApp().run()