# ui/dashboard.py — Page sections for the Awareness Companion dashboard.
#
# Composes the primitives from ui/widgets.py into the page sections shown
# in the design (status bar, header, sensor cards, recent alerts, log modal).
# All data logic lives in ui/data.py and the services.

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from ui.theme import (
    alpha, TEXT, MUTED, BORDER, SECONDARY, MINT, AMBER,
    FONT_LABEL, FONT_CAPTION, RADIUS_TILE,
)
from ui.data import (TONE_COLORS, SENSOR_BY_ID, format_value, format_event_value,
                     format_when, format_exact)
from ui.icons import IconWidget
from ui.widgets import (
    RoundedCard, Pill, IconTile, ThresholdSlider, EventRow, Modal,
    BatteryGlyph, Divider, autosize, keep_centered, TRACK_INSET,
)


# ─────────────────────────────────────────────
# STATUS BAR — connection toggle + battery level pills
# ─────────────────────────────────────────────
class StatusBar(BoxLayout):
    """Top-right pill row: connection toggle and battery level."""

    def __init__(self, on_toggle_connection=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.height = dp(36)
        self.spacing = dp(8)
        self.orientation = "horizontal"
        self._on_toggle_connection = on_toggle_connection

        # Cached glyphs reused across pill updates
        self._bt_on = IconWidget(name="bluetooth", color=MINT,
                                 size=(dp(14), dp(16)), stroke=dp(1.0))
        self._bt_off = IconWidget(name="bluetooth", color=MUTED,
                                  size=(dp(14), dp(16)), stroke=dp(1.0))
        self._bat_glyph = BatteryGlyph(pct=62, color=MINT)

        self._connect_pill = Pill(text="Connected", icon=self._bt_on,
                                  fg=MINT, bg=alpha(MINT, 0.12),
                                  ring=alpha(MINT, 0.35))
        self._connect_pill.on_press = self._toggle
        self.add_widget(self._connect_pill)

        self._battery_pill = Pill(text="--%", icon=self._bat_glyph,
                                  fg=TEXT, bg=SECONDARY, ring=BORDER)
        self.add_widget(self._battery_pill)
        self._fit()

        self._connected_state = None
        self._battery_state = None

    def add_widget(self, widget, *args, **kwargs):
        super().add_widget(widget, *args, **kwargs)
        widget.bind(size=self._fit)

    def _fit(self, *_):
        """Keep the bar exactly as wide as its pills so the battery pill
        never overflows the window edge."""
        width = sum(c.width for c in self.children)
        if len(self.children) > 1:
            width += self.spacing * (len(self.children) - 1)
        if self.width != width:
            self.width = width

    def _toggle(self):
        if self._on_toggle_connection:
            self._on_toggle_connection()

    def set_connected(self, connected):
        """Show the connection pill in its connected / disconnected state."""
        if connected == self._connected_state:
            return
        self._connected_state = connected
        if connected:
            self._connect_pill.set(text="Connected", fg=MINT,
                                   bg=alpha(MINT, 0.12), ring=alpha(MINT, 0.35),
                                   icon=self._bt_on)
        else:
            self._connect_pill.set(text="Disconnected", fg=MUTED,
                                   bg=SECONDARY, ring=BORDER, icon=self._bt_off)

    def set_battery(self, pct):
        """Show the battery level pill; pct < 0 renders as 'N/A'."""
        if pct is not None and pct < 0:
            pct = None
        if pct == self._battery_state:
            return
        self._battery_state = pct
        if pct is None:
            self._bat_glyph.update(0, AMBER)
            self._battery_pill.set(text="N/A", fg=MUTED, bg=SECONDARY,
                                   ring=BORDER, icon=self._bat_glyph)
            return
        color = MINT if pct > 20 else AMBER
        self._bat_glyph.update(pct, color)
        self._battery_pill.set(text=f"{pct:.0f}%", fg=TEXT, bg=SECONDARY,
                               ring=BORDER, icon=self._bat_glyph)


# ─────────────────────────────────────────────
# HEADER — "Awareness / Wearable" title at the top-left corner
# ─────────────────────────────────────────────
class HeaderSection(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.height = dp(56)
        title = Label(text="Awareness\n[b]Wearable[/b]", markup=True,
                      font_size='20sp', color=TEXT,
                      size_hint=(None, None), valign="middle")
        # Size the label to its text and the header to the label, so the
        # title starts at the same left offset as the sensor cards
        title.bind(texture_size=lambda w, s: setattr(w, "size", s))
        self.add_widget(keep_centered(title))
        self.width = title.width
        title.bind(size=lambda w, s: setattr(self, "width", w.width))


# ─────────────────────────────────────────────
# SENSOR CARD — icon + hint, status pill, threshold slider on the scale,
# live reading and the last alert caption
# ─────────────────────────────────────────────
class SensorCard(RoundedCard):
    def __init__(self, sensor, on_threshold=None, **kwargs):
        super().__init__(**kwargs)
        self._sensor = sensor
        self.sensor = sensor  # public for the hover tooltip
        self._on_threshold = on_threshold
        self._status_state = None
        self.spacing = dp(10)
        tone = TONE_COLORS[sensor.tone]

        # ── Top row: icon tile + name/hint, status pill on the right ──
        top = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(56), spacing=dp(12))
        tile = IconTile(icon=sensor.icon, tone=tone, size=44,
                        radius=RADIUS_TILE)
        top.add_widget(keep_centered(tile))

        names = BoxLayout(orientation="vertical")
        name = autosize(Label(text=sensor.label, font_size=FONT_LABEL,
                              color=TEXT, bold=True, size_hint=(None, None)))
        names.add_widget(name)
        top.add_widget(names)
        # Sensor name hover target (the hint text shows as a tooltip)
        self._name_lbl = name

        def _align_name(*_):
            # Vertically center the sensor name on the icon tile. A vertical
            # BoxLayout stacks its single child from the bottom, so the
            # offset must be applied as bottom padding.
            icon_cy = tile.center_y
            offset = max(0.0, icon_cy - name.height / 2 - names.y)
            names.padding = [0, 0, 0, offset]

        name.bind(height=lambda w, h: _align_name())
        top.bind(pos=lambda w, p: _align_name())
        top.bind(size=lambda w, s: _align_name())

        # Status pill icons are cached and swapped through Pill.set()
        self._icon_alert = IconWidget(name="alert", color=AMBER,
                                      size=(dp(14), dp(14)))
        self._icon_ok = IconWidget(name="check", color=MINT,
                                   size=(dp(14), dp(14)))
        self._status_pill = Pill(text="No alerts", icon=self._icon_ok,
                                 fg=MINT, bg=alpha(MINT, 0.12),
                                 ring=alpha(MINT, 0.30))
        top.add_widget(keep_centered(self._status_pill))
        self.add_widget(top)

        # ── Slider drawn on the sensor scale ──
        self._slider = ThresholdSlider(min_val=sensor.min, max_val=sensor.max,
                                       step=sensor.step,
                                       value=sensor.default_threshold, tone=tone)
        self._slider.on_value_change = self._on_slider
        self.add_widget(self._slider)

        # ── Scale row: min · set value · max, all on the track line ──
        self._min_lbl = autosize(Label(
            text=format_value(sensor.id, sensor.min), font_size=FONT_CAPTION,
            color=MUTED, size_hint=(None, None)))
        self._value_lbl = autosize(Label(text="", font_size='14sp', color=TEXT,
                                         bold=True, size_hint=(None, None)))
        self._unit_lbl = autosize(Label(text="", font_size='12sp',
                                        color=MUTED, size_hint=(None, None)))
        self._max_lbl = autosize(Label(
            text=format_value(sensor.id, sensor.max), font_size=FONT_CAPTION,
            color=MUTED, size_hint=(None, None)))
        value_group = BoxLayout(orientation="horizontal", spacing=dp(4),
                                size_hint=(None, None))
        value_group.add_widget(self._value_lbl)
        value_group.add_widget(self._unit_lbl)
        self._value_group = value_group

        scale_row = FloatLayout(size_hint_y=None, height=dp(18))
        scale_row.add_widget(self._min_lbl)
        scale_row.add_widget(value_group)
        scale_row.add_widget(self._max_lbl)

        def _layout_scale(*_):
            # Place min / set value / max along the slider track, with the
            # set value always centered between the two scale ends
            track_x = scale_row.x + dp(TRACK_INSET)
            track_w = scale_row.width - dp(TRACK_INSET) * 2
            self._min_lbl.y = scale_row.y + (scale_row.height
                                             - self._min_lbl.height) / 2
            self._min_lbl.x = track_x
            value_group.pos = (track_x + track_w / 2 - value_group.width / 2,
                               scale_row.y + (scale_row.height
                                              - value_group.height) / 2)
            self._max_lbl.y = scale_row.y + (scale_row.height
                                             - self._max_lbl.height) / 2
            self._max_lbl.x = track_x + track_w - self._max_lbl.width

        def _fit_group(*_):
            # Size the group to its labels, then re-position on the track
            value_group.width = (self._value_lbl.width + self._unit_lbl.width
                                 + value_group.spacing)
            value_group.height = max(self._value_lbl.height,
                                     self._unit_lbl.height)
            _layout_scale()

        self._layout_scale = _layout_scale
        self._value_lbl.bind(size=_fit_group)
        self._unit_lbl.bind(size=_fit_group)
        self._min_lbl.bind(size=_fit_group)
        self._max_lbl.bind(size=_fit_group)
        scale_row.bind(pos=_layout_scale, size=_layout_scale)
        self.add_widget(scale_row)
        _fit_group()

        # ── Last alert caption ──
        self._last_lbl = Label(text="No alerts recorded yet",
                               font_size=FONT_CAPTION, color=MUTED,
                               size_hint_y=None, height=dp(16), halign="left")
        self.add_widget(self._last_lbl)

        self.set_threshold(sensor.default_threshold)

    # ── Slider callback ──
    def _on_slider(self, value):
        self.set_threshold(value)
        if self._on_threshold:
            self._on_threshold(self._sensor.id, value)

    # ── Public update API (called by the app loop) ──
    def name_rect_content(self):
        """Rect of the sensor name in the scroll-content coordinates
        (the space the scrollview's to_local() produces), or None."""
        lbl = self._name_lbl
        if lbl is None or lbl.width == 0:
            return None
        return (lbl.x, lbl.y, lbl.width, lbl.height)

    def set_threshold(self, value):
        self._slider.set_value(value)
        self._value_lbl.text = f"{value:g}"
        self._unit_lbl.text = self._sensor.unit
        self._layout_scale()

    def set_last_alert(self, event):
        if event is None:
            self._last_lbl.text = "No alerts recorded yet"
        else:
            self._last_lbl.text = (
                f"Last alert: {format_event_value(self._sensor.id, event.value)}"
                f" · {format_when(event.at)}"
            )

    def set_status(self, state):
        """state: 'ok' (no alerts), 'recent' (alert within the hour) or
        'no_signal' (device disconnected)."""
        if state == self._status_state:
            return
        self._status_state = state
        if state == "recent":
            self._status_pill.opacity = 1
            self._status_pill.set(text="Recent alert", fg=AMBER,
                                  bg=alpha(AMBER, 0.15),
                                  ring=alpha(AMBER, 0.35), icon=self._icon_alert)
        elif state == "no_signal":
            # No pill while disconnected: the connection pill in the top
            # bar already carries that state
            self._status_pill.opacity = 0
        else:
            self._status_pill.opacity = 1
            self._status_pill.set(text="No alerts", fg=MINT,
                                  bg=alpha(MINT, 0.12),
                                  ring=alpha(MINT, 0.30), icon=self._icon_ok)


# ─────────────────────────────────────────────
# RECENT ALERTS CARD — heading, 'View full week' button and alert rows
# ─────────────────────────────────────────────
class RecentAlertsCard(RoundedCard):
    def __init__(self, on_open_log=None, **kwargs):
        super().__init__(**kwargs)
        self._on_open_log = on_open_log
        self.spacing = dp(8)

        head = BoxLayout(orientation="horizontal", size_hint_y=None,
                         height=dp(40), spacing=dp(8))
        head.add_widget(keep_centered(autosize(Label(
            text="RECENT ALERTS", font_size='13sp', bold=True, color=MUTED,
            size_hint=(None, None)))))
        head.add_widget(Widget())  # spacer
        self._history_icon = IconWidget(name="history", color=TEXT,
                                        size=(dp(14), dp(14)))
        self._week_btn = Pill(text="View full week", fg=TEXT, bg=SECONDARY,
                              ring=BORDER, height=36, icon=self._history_icon)
        self._week_btn.on_press = self._open_log
        head.add_widget(keep_centered(self._week_btn))
        self.add_widget(head)

        self._rows = BoxLayout(orientation="vertical", size_hint_y=None,
                               spacing=dp(8))
        self._rows.bind(minimum_height=self._rows.setter("height"))
        self.add_widget(self._rows)
        self.set_events([])

    def _open_log(self):
        if self._on_open_log:
            self._on_open_log()

    def set_events(self, events):
        """Rebuild the visible rows (the design shows the four newest alerts)."""
        self._rows.clear_widgets()
        if not events:
            self._rows.add_widget(Label(text="No alerts yet",
                                        font_size=FONT_CAPTION, color=MUTED,
                                        size_hint_y=None, height=dp(36),
                                        halign="center"))
            return
        for i, event in enumerate(events):
            if i:
                self._rows.add_widget(Divider())
            self._rows.add_widget(EventRow(
                sensor=SENSOR_BY_ID[event.sensor], event=event,
                when_text=format_when(event.at)))


# ─────────────────────────────────────────────
# FOOTER — last-sync note
# ─────────────────────────────────────────────
class FooterLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Awareness Wearable · last sync moments ago"
        self.font_size = FONT_CAPTION
        self.color = MUTED
        self.size_hint_y = None
        self.height = dp(28)
        self.halign = "center"
        self.valign = "middle"
        self.bind(size=lambda w, s: setattr(w, "text_size", s))

    def set_connected(self, connected):
        self.text = ("Awareness Wearable · last sync moments ago"
                     if connected else "Awareness Wearable · last sync 2 h ago")


# ─────────────────────────────────────────────
# FULL LOG MODAL — bottom sheet with the complete alert history
# ─────────────────────────────────────────────
class FullLogModal(Modal):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Header: title + subtitle on the left, close button on the right
        title_col = BoxLayout(orientation="vertical", spacing=dp(1))
        title_col.add_widget(autosize(Label(text="Full alert log",
                                            font_size=FONT_LABEL, color=TEXT,
                                            bold=True, size_hint=(None, None))))
        title_col.add_widget(autosize(Label(text="Last 7 days",
                                            font_size=FONT_CAPTION, color=MUTED,
                                            size_hint=(None, None))))
        self._header.add_widget(keep_centered(title_col))
        self._header.add_widget(Widget())  # spacer
        self._close_icon = IconWidget(name="close", color=TEXT,
                                      size=(dp(16), dp(16)))
        self._close_btn = Pill(text="", icon=self._close_icon, fg=TEXT,
                               bg=SECONDARY, ring=BORDER, height=40)
        self._close_btn.on_press = self.close
        self._header.add_widget(keep_centered(self._close_btn))

        self._rows = BoxLayout(
            orientation="vertical", size_hint_y=None,
            # Same margins/padding as the recent-log rows on the page
            padding=[dp(16), dp(14), dp(16), dp(14)],
            spacing=dp(8))
        self._rows.bind(minimum_height=self._rows.setter("height"))
        self._content.add_widget(self._rows)

    def open(self, events):
        self.set_events(events)
        super().open()

    def set_events(self, events):
        """Rebuild the full log rows with exact timestamps."""
        self._rows.clear_widgets()
        if not events:
            self._rows.add_widget(Label(text="No alerts yet",
                                        font_size=FONT_CAPTION, color=MUTED,
                                        size_hint_y=None, height=dp(36),
                                        halign="center"))
            return
        for i, event in enumerate(events):
            if i:
                self._rows.add_widget(Divider())
            self._rows.add_widget(EventRow(
                sensor=SENSOR_BY_ID[event.sensor], event=event,
                when_text=format_exact(event.at)))
