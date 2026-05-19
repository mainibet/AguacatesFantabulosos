# main.py — AwarenessApp entry point

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle, Ellipse
from kivy.core.text import LabelBase

from ui.theme import (
    ACCENT, TEXT, BORDER, BAR_BG, WINDOW_SIZE, POLL_INTERVAL,
    DB_MIN, DB_MAX, DANGER, DEFAULT_THRESH_LIGHT, DEFAULT_THRESH_CROWDNESS
)
from ui.widgets import Card, NoiseBar, LogList
from services.ble       import BLEMonitor
from services.battery   import BatteryMonitor
from services.crowdness import CrowdnessMonitor
from ui.dashboard       import BatteryCard, SensorMiniCard

# Emoji en macOS
LabelBase.register(
    name='Emoji',
    fn_regular='/System/Library/Fonts/Apple Color Emoji.ttc'
)

Window.clearcolor = (0.059, 0.067, 0.082, 1)
Window.size = WINDOW_SIZE

PURPLE = (0.427, 0.176, 0.431, 1)

def _pct(value):
    return max(0.0, min(1.0, (value - DB_MIN) / (DB_MAX - DB_MIN)))


class ThresholdSlider(Widget):
    def __init__(self, min_val=40, max_val=100, value=75, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(40)
        self.min_val = min_val
        self.max_val = max_val
        self._value = value
        self.on_value_change = None
        self._dragging = False
        self.bind(pos=self._redraw, size=self._redraw)

    @property
    def value(self):
        return self._value

    def _track_x(self):
        return self.x + dp(12)

    def _track_w(self):
        return self.width - dp(24)

    def _thumb_x(self):
        pct = (self._value - self.min_val) / (self.max_val - self.min_val)
        return self._track_x() + pct * self._track_w()

    def _redraw(self, *_):
        self.canvas.clear()
        cx      = self._thumb_x()
        ty      = self.center_y
        track_h = dp(6)
        radius  = [track_h / 2]
        thumb_r = dp(11)
        with self.canvas:
            Color(*BAR_BG)
            RoundedRectangle(
                pos=(self._track_x(), ty - track_h / 2),
                size=(self._track_w(), track_h),
                radius=radius
            )
            filled_w = cx - self._track_x()
            if filled_w > 0:
                Color(*PURPLE)
                RoundedRectangle(
                    pos=(self._track_x(), ty - track_h / 2),
                    size=(filled_w, track_h),
                    radius=radius
                )
            Color(*PURPLE)
            Ellipse(pos=(cx - thumb_r, ty - thumb_r), size=(thumb_r * 2, thumb_r * 2))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._dragging = True
            self._update_from_touch(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._dragging:
            self._update_from_touch(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._dragging:
            self._dragging = False
            return True
        return super().on_touch_up(touch)

    def _update_from_touch(self, touch):
        pct = max(0.0, min(1.0, (touch.x - self._track_x()) / self._track_w()))
        self._value = self.min_val + pct * (self.max_val - self.min_val)
        if self.on_value_change:
            self.on_value_change(self._value)
        self._redraw()


class RootLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(0)

        self._dot_count = 0
        self._threshold = 75.0
        self._alerted   = False

        self._battery   = BatteryMonitor()
        self._crowdness = CrowdnessMonitor()
        self._ble       = BLEMonitor()
        self._ble.start()

        self._build_ui()
        Clock.schedule_interval(self._tick, POLL_INTERVAL)

    def _build_ui(self):

        # 1. Header
        header = BoxLayout(size_hint_y=None, height=dp(44))

        app_name = Label(
            text="AwarenessApp",
            font_size='18sp',
            bold=True,
            color=TEXT,
            halign='left',
            valign='middle',
        )
        app_name.bind(size=lambda w, s: setattr(w, 'text_size', s))
        header.add_widget(app_name)

        # badge = el pill de "CONNECTED" / "DISCONNECTED" arriba a la derecha
        self._badge = Label(
            text="CONNECTED",
            font_size='12sp',
            color=ACCENT,
            size_hint=(None, None),
            size=(dp(124), dp(30)),
            halign='center',
            valign='middle',
        )
        self._badge.text_size = (dp(124), dp(30))

        with self._badge.canvas.before:
            Color(*ACCENT)
            self._badge_line = Line(
                rounded_rectangle=(0, 0, dp(124), dp(30), dp(15)),
                width=1.2
            )

        self._badge.bind(
            pos=lambda w, _: setattr(
                self._badge_line,
                'rounded_rectangle',
                (w.x, w.y, w.width, w.height, dp(15))
            )
        )

        header.add_widget(self._badge)
        self.add_widget(header)

        self.add_widget(Widget(size_hint_y=None, height=dp(14)))

        # 2. Batería
        self._batt_card = BatteryCard()
        self.add_widget(self._batt_card)

        self.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # 3. Luz + Crowdness
        row = BoxLayout(size_hint_y=None, height=dp(90), spacing=dp(10))
        self._light_card = SensorMiniCard("LIGHT", " lux")
        self._crowd_card = SensorMiniCard("CROWDNESS", "%")
        row.add_widget(self._light_card)
        row.add_widget(self._crowd_card)
        self.add_widget(row)

        self.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # 4. Noise card
        level_card = Card(size_hint_y=None, height=dp(152))

        level_card.add_widget(Label(
            text="CURRENT NOISE LEVEL",
            font_size='15sp',
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(22),
            halign='center',
            valign='middle',
        ))

        self._status_lbl = Label(
            text="Waiting for BLE data...",
            font_size='12sp',
            color=(1, 1, 1, 0.6),
            size_hint_y=None,
            height=dp(18),
            halign='center',
            valign='middle',
        )
        level_card.add_widget(self._status_lbl)

        self._db_lbl = Label(
            text="-- dB",
            font_size='22sp',
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(36),
            halign='center',
            valign='middle',
        )
        level_card.add_widget(self._db_lbl)
        self.add_widget(level_card)

        self.add_widget(Widget(size_hint_y=None, height=dp(14)))

        # 5. Threshold card
        thresh_card = Card(size_hint_y=None, height=dp(134))

        thresh_card.add_widget(Label(
            text="THRESHOLD",
            font_size='15sp',
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(22),
            halign='center',
            valign='middle',
        ))

        self._slider = ThresholdSlider(min_val=40, max_val=100, value=75)
        self._slider.on_value_change = self._on_slider
        thresh_card.add_widget(self._slider)

        self._thresh_lbl = Label(
            text="75 dB",
            font_size='22sp',
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(36),
            halign='center',
            valign='middle',
        )
        thresh_card.add_widget(self._thresh_lbl)
        self.add_widget(thresh_card)

        self.add_widget(Widget(size_hint_y=None, height=dp(18)))

        # 6. Log
        log_box = BoxLayout(orientation='vertical', spacing=dp(6))

        log_box.add_widget(Label(
            text="EVENT LOG",
            font_size='13sp',
            bold=True,
            color=TEXT,
            size_hint_y=None,
            height=dp(26),
        ))

        self._empty_lbl = Label(
            text="No events yet.",
            font_size='12sp',
            color=(1, 1, 1, 0.4),
            size_hint_y=None,
            height=dp(32),
        )
        log_box.add_widget(self._empty_lbl)

        scroll = ScrollView()
        self._log_list = LogList()
        scroll.add_widget(self._log_list)
        log_box.add_widget(scroll)

        self.add_widget(log_box)

    # ─────────────────────────────────────────────
    # BLE STATUS
    # ─────────────────────────────────────────────

    def _update_ble_status(self):
        if self._ble.connected:
            self._badge.text  = "CONNECTED"
            self._badge.color = ACCENT
        else:
            self._badge.text  = "DISCONNECTED"
            self._badge.color = DANGER

    # ─────────────────────────────────────────────
    # EVENTS
    # ─────────────────────────────────────────────

    def _on_slider(self, value):
        self._threshold = value
        self._thresh_lbl.text = f"{value:.0f} dB"

    # ─────────────────────────────────────────────
    # MAIN LOOP
    # ─────────────────────────────────────────────

    def _tick(self, dt):

        # Dots animation
        self._dot_count = (self._dot_count + 1) % 4
        self._status_lbl.text = f"Waiting for BLE data{'.' * self._dot_count}"

        # Badge BLE
        self._update_ble_status()

        # Batería
        batt = self._battery.get()
        self._batt_card.update(batt["percent"])

        # Crowdness dummy
        self._crowd_card.update(self._crowdness.update(), DEFAULT_THRESH_CROWDNESS)

        # BLE
        if self._ble.last_alert:
            msg = self._ble.last_alert
            self._ble.last_alert = None
            try:
                data = self._ble.parse_ble(msg)

                if "noise" in data:
                    value = data["noise"]
                    self._db_lbl.text = f"{value:.0f} dB"
                    self._log_list.add_event(value)
                    self._alerted = value > self._threshold
                    if self._alerted:
                        self._empty_lbl.opacity = 0

                if "light" in data:
                    self._light_card.update(data["light"], DEFAULT_THRESH_LIGHT)

            except Exception as e:
                print("BLE parse error:", e)


class AwarenessApp(App):
    def build(self):
        return RootLayout()


if __name__ == "__main__":
    AwarenessApp().run()