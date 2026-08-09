# app/main.py — Awareness Wearable companion app (Kivy).
#
# Implements the "Awareness Companion" dashboard design. UI sections live in
# ui/dashboard.py, primitives in ui/widgets.py, sensor/event data in
# ui/data.py and device services in services/.

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

from ui.theme import BG, WINDOW_SIZE, POLL_INTERVAL
from ui.data import EventsStore, SENSORS, DEFAULT_THRESHOLDS, LIGHT_LEVEL_LUX
from ui.dashboard import (
    StatusBar, HeaderSection, SensorCard, RecentAlertsCard,
    FooterLabel, FullLogModal,
)
from ui.widgets import AwarenessScrollView, Tooltip, keep_centered
from services.ble import BLEMonitor
from services.battery import BatteryMonitor
from services.crowdness import CrowdnessMonitor


Window.clearcolor = BG
Window.size = WINDOW_SIZE


class RootLayout(FloatLayout):
    """Wires the services to the dashboard sections and runs the poll loop."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ── State ──
        self._thresholds = dict(DEFAULT_THRESHOLDS)
        self._live = {s.id: None for s in SENSORS}
        self._was_above = {s.id: False for s in SENSORS}
        self._events = EventsStore()
        self._events.seed_demo()
        self._connected = False
        self._connected_manual = False   # True after the user taps the pill
        self._last_battery = None

        # ── Services ──
        self._battery = BatteryMonitor()
        self._crowdness = CrowdnessMonitor()
        self._crowdness.start()
        self._ble = BLEMonitor()
        self._ble.start()

        self._build_ui()
        Clock.schedule_interval(self._tick, POLL_INTERVAL)

    # ─────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────
    def _build_ui(self):
        # Scrollable page content
        content = BoxLayout(orientation="vertical", size_hint_y=None,
                            padding=[dp(20), dp(28), dp(20), dp(28)],
                            spacing=dp(16))
        content.bind(minimum_height=content.setter("height"))
        scroll = AwarenessScrollView()
        scroll.add_widget(content)
        self.add_widget(scroll)
        self._scroll = scroll

        # 1. Top row: app name at the top-left, status pills top-right
        self._status_bar = StatusBar(on_toggle_connection=self._toggle_connection)
        top_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                            height=dp(56), spacing=dp(12))
        top_row.add_widget(keep_centered(HeaderSection()))
        top_row.add_widget(Widget())  # spacer pushes the pills to the right
        top_row.add_widget(keep_centered(self._status_bar))
        content.add_widget(top_row)

        # 2. Sensor cards
        self._cards = {}
        for s in SENSORS:
            card = SensorCard(sensor=s, on_threshold=self._on_threshold_change)
            self._cards[s.id] = card
            content.add_widget(card)

        # 3. Recent alerts
        self._recent_card = RecentAlertsCard(on_open_log=self._open_log)
        content.add_widget(self._recent_card)

        # 5. Footer
        self._footer = FooterLabel()
        content.add_widget(self._footer)

        # Full alert log overlay (on top of the scrollable page)
        self._modal = FullLogModal()
        self.add_widget(self._modal)

        # Hover tooltip (sensor hints), topmost layer
        self._tooltip = Tooltip()
        self.add_widget(self._tooltip)
        Window.bind(mouse_pos=self._update_tooltip)

    # ─────────────────────────────────────────────
    # HOVER TOOLTIP — sensor hint over the sensor name
    # ─────────────────────────────────────────────
    def _update_tooltip(self, window, pos):
        if self._modal._open:
            self._tooltip.hide()
            return
        # Convert the mouse to content coordinates (matches the slider
        # capture path) and hit-test the sensor name labels
        mx, my = self._scroll.to_local(*pos)
        for card in self._cards.values():
            rect = card.name_rect_content()
            if rect and rect[0] <= mx <= rect[0] + rect[2] \
                    and rect[1] <= my <= rect[1] + rect[3]:
                self._tooltip.show(card.sensor.hint, *pos)
                return
        self._tooltip.hide()

    # ─────────────────────────────────────────────
    # THRESHOLDS AND EVENTS
    # ─────────────────────────────────────────────
    def _on_threshold_change(self, sensor_id, value):
        self._thresholds[sensor_id] = value
        self._refresh_cards()

    def _check_crossing(self, sensor_id, value):
        """Log an alert when the value rises above the threshold
        (edge-triggered, so a sustained over-threshold reading logs once)."""
        above = value >= self._thresholds[sensor_id]
        if above and not self._was_above[sensor_id]:
            self._events.add(sensor_id, value, self._thresholds[sensor_id])
        self._was_above[sensor_id] = above

    # ─────────────────────────────────────────────
    # CONNECTION AND BATTERY
    # ─────────────────────────────────────────────
    def _toggle_connection(self):
        self._connected = not self._connected
        self._connected_manual = True

    def _update_connection(self):
        """A real BLE connection always wins; otherwise the demo toggle
        the user tapped stands."""
        if self._ble.connected:
            self._connected = True
            self._connected_manual = False
        elif not self._connected_manual:
            self._connected = False
        self._status_bar.set_connected(self._connected)
        self._footer.set_connected(self._connected)

    def _update_battery(self):
        # Prefer the device reading, fall back to the OS battery
        if self._ble.last_bat is not None:
            parsed = self._ble.parse_bat(self._ble.last_bat)
            self._ble.last_bat = None
            if parsed is not None:
                self._last_battery = parsed
        pct = self._last_battery
        if pct is None:
            pct = self._battery.get()["percent"]
        self._status_bar.set_battery(pct)

    # ─────────────────────────────────────────────
    # MAIN LOOP
    # ─────────────────────────────────────────────
    def _tick(self, dt):
        # Connection status
        self._update_connection()

        # Battery
        self._update_battery()

        # Noise (BLE)
        if self._ble.last_sound is not None:
            val = self._ble.parse_sound(self._ble.last_sound)
            self._ble.last_sound = None
            if val is not None:
                self._live["noise"] = float(val)
                self._check_crossing("noise", float(val))

        # Light (BLE, three levels → lux)
        if self._ble.last_light is not None:
            level = self._ble.parse_light(self._ble.last_light)
            self._ble.last_light = None
            if level is not None and level in LIGHT_LEVEL_LUX:
                lux = float(LIGHT_LEVEL_LUX[level])
                self._live["light"] = lux
                self._check_crossing("light", lux)

        # Crowdness (BLE adjacency estimation)
        crowd = self._crowdness.update()
        if crowd is not None:
            self._live["crowdness"] = crowd
            self._check_crossing("crowdness", crowd)

        # Refresh every card and the recent alert list
        self._refresh_cards()
        self._recent_card.set_events(self._events.recent(4))

    def _refresh_cards(self):
        for sid, card in self._cards.items():
            card.set_threshold(self._thresholds[sid])
            card.set_last_alert(self._events.last_for(sid))
            if not self._connected:
                card.set_status("no_signal")
            elif self._events.is_recent_alert(sid, self._thresholds[sid]):
                card.set_status("recent")
            else:
                card.set_status("ok")

    # ─────────────────────────────────────────────
    # MODAL
    # ─────────────────────────────────────────────
    def _open_log(self):
        self._modal.open(self._events.all())

    # ─────────────────────────────────────────────
    # SHUTDOWN — stop background services cleanly
    # ─────────────────────────────────────────────
    def stop_services(self):
        """Stop every background thread so the interpreter exits without
        crashing (macOS otherwise reports an unexpected quit)."""
        self._crowdness.stop()
        self._ble.stop()


class AwarenessApp(App):
    def build(self):
        return RootLayout()

    def on_request_close(self, *args):
        """Always allow the window to close (red X) and trigger the clean
        shutdown immediately."""
        Clock.schedule_once(lambda dt: self.stop(), 0)
        return False

    def on_stop(self):
        """Clean shutdown: join the BLE/crowdness threads before the
        interpreter exits (prevents the macOS 'unexpectedly quit' dialog)."""
        if self.root is not None:
            self.root.stop_services()


if __name__ == "__main__":
    AwarenessApp().run()
    pass