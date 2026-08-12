# ui/data.py and device services in services/.

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

from ui.theme import BG, WINDOW_SIZE, POLL_INTERVAL
from ui.data import (EventsStore, SENSORS, DEFAULT_THRESHOLDS, LIGHT_LEVEL_LUX,
                     NOISE_LEVEL_DB, CROWD_LEVEL_PPM)
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
        self._config_dirty = True        # push thresholds on the first connect
        self._cleared_demo = False       # demo alerts dropped on first connect

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
        # Re-arm the crossing detector: a reading that is above the NEW
        # threshold must alert again (e.g. lowering the threshold while the
        # sensor is already over it).
        self._was_above[sensor_id] = False
        # Re-evaluate the latest reading against the new threshold right
        # away — the device may not send again until its next cycle.
        # Throttled to 30s so dragging a slider through many values logs
        # one alert, not one per snap.
        live = self._live.get(sensor_id)
        if live is not None:
            age = self._events.last_event_seconds_ago(sensor_id)
            if age is None or age > 30.0:
                self._check_crossing(sensor_id, live)
        self._config_dirty = True   # the device gates its alerts on this
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
        # Demo affordance only: with a real BLE backend the pill reflects
        # the actual device connection, so manual toggling is disabled.
        if self._ble.capable:
            return
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

        # First real device connection: drop the seeded demo alerts so the
        # dashboard only ever shows real events once live data is flowing.
        if self._ble.connected and not self._cleared_demo:
            self._cleared_demo = True
            self._events.clear()
            self._was_above = {s.id: False for s in SENSORS}

        # The device only notifies when its threshold is exceeded, so push
        # the app thresholds over BLE whenever they change (or on connect).
        if self._connected and self._config_dirty:
            self._config_dirty = False
            msg = (f"noise={self._thresholds['noise']:g}"
                   f";light={self._thresholds['light']:g}")
            self._ble.push_config(msg)

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

        # Noise (BLE, traffic-light levels → dB)
        if self._ble.last_sound is not None:
            level = self._ble.parse_sound(self._ble.last_sound)
            self._ble.last_sound = None
            if level is not None and level in NOISE_LEVEL_DB:
                db = float(NOISE_LEVEL_DB[level])
                self._live["noise"] = db
                self._check_crossing("noise", db)

        # Light (BLE, three levels → lux)
        if self._ble.last_light is not None:
            level = self._ble.parse_light(self._ble.last_light)
            self._ble.last_light = None
            if level is not None and level in LIGHT_LEVEL_LUX:
                lux = float(LIGHT_LEVEL_LUX[level])
                self._live["light"] = lux
                self._check_crossing("light", lux)

        # Crowdness: prefer the device's traffic-light count (phone and
        # desktop), fall back to the local BLE-adjacency estimate (desktop
        # only) when no device crowd data has arrived.
        if self._ble.last_crowd is not None:
            level = self._ble.parse_crowd(self._ble.last_crowd)
            self._ble.last_crowd = None
            if level is not None and level in CROWD_LEVEL_PPM:
                ppm = float(CROWD_LEVEL_PPM[level])
                self._live["crowdness"] = ppm
                self._check_crossing("crowdness", ppm)
        else:
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
            elif self._events.is_recent_alert(sid):
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