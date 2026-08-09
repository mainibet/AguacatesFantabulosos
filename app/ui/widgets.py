# ui/widgets.py — Reusable primitives for the Awareness Companion dashboard.
#
# Composition-only widgets: each one draws itself with canvas instructions
# and exposes a small update API. The page sections live in ui/dashboard.py.

from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.core.window import Window

from ui.theme import (
    alpha, BG, CARD, SURFACE, BORDER, SECONDARY, TEXT, MUTED, AMBER, MINT,
    SKY, FONT_BODY, FONT_CAPTION, RADIUS_CARD, RADIUS_TILE, RADIUS_ROW,
)
from ui.data import format_value
from ui.icons import IconWidget


# ─────────────────────────────────────────────
# LABEL HELPERS
# ─────────────────────────────────────────────
def autosize(label):
    """Let a Label shrink to fit its text (for use inside BoxLayout rows)."""
    label.bind(texture_size=lambda w, s: setattr(w, "size", s))
    return label


# ─────────────────────────────────────────────
# CARD — raised surface with rounded corners, hairline border and shadow
# ─────────────────────────────────────────────
class RoundedCard(BoxLayout):
    """Card surface that auto-sizes to its content height."""

    def __init__(self, radius=RADIUS_CARD, **kwargs):
        super().__init__(**kwargs)
        self._radius = dp(radius)
        self.orientation = "vertical"
        self.padding = [dp(16), dp(14), dp(16), dp(14)]
        self.spacing = dp(8)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))

        with self.canvas.before:
            # Soft drop shadow: two translucent layers offset downwards
            Color(0, 0, 0, 0.30)
            self._shadow = RoundedRectangle(pos=(0, 0), size=(0, 0),
                                            radius=[self._radius])
            Color(0, 0, 0, 0.16)
            self._shadow_far = RoundedRectangle(pos=(0, 0), size=(0, 0),
                                                radius=[self._radius])
            Color(*CARD)
            self._rect = RoundedRectangle(pos=(0, 0), size=(0, 0),
                                          radius=[self._radius])
            Color(*BORDER)
            self._ring = Line(rounded_rectangle=(0, 0, 0, 0, self._radius),
                              width=1.1)
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *_):
        self._shadow.pos = (self.x, self.y - dp(5))
        self._shadow.size = self.size
        self._shadow_far.pos = (self.x, self.y - dp(9))
        self._shadow_far.size = self.size
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._ring.rounded_rectangle = (self.x, self.y, self.width, self.height,
                                        self._radius)


# ─────────────────────────────────────────────
# ICON TILE — rounded square with tinted fill and ring around an icon
# ─────────────────────────────────────────────
class IconTile(FloatLayout):
    """Small rounded square holding a line icon, tinted with a sensor tone.
    The icon is centered in the tile."""

    def __init__(self, icon, tone, size=44, radius=RADIUS_TILE, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(size), dp(size))
        self._radius = dp(radius)
        with self.canvas.before:
            Color(*alpha(tone, 0.12))
            self._fill = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[self._radius])
            Color(*alpha(tone, 0.30))
            self._ring = Line(rounded_rectangle=(0, 0, 0, 0, self._radius),
                              width=1.1)
        icon_size = dp(size * 0.5)
        icon_w = IconWidget(name=icon, color=tone,
                            size=(icon_size, icon_size),
                            size_hint=(None, None))
        icon_w.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.add_widget(icon_w)
        self.bind(pos=self._update, size=self._update)
        self._update()

    def _update(self, *_):
        self._fill.pos = self.pos
        self._fill.size = self.size
        self._ring.rounded_rectangle = (self.x, self.y, self.width, self.height,
                                        self._radius)


# ─────────────────────────────────────────────
# PILL — rounded status pill: optional icon + label, tinted fill and ring
# ─────────────────────────────────────────────
class Pill(FloatLayout):
    """Auto-width pill. Call set() to change content/colors and assign
    `on_press` to make it tappable. Children are centered vertically."""

    def __init__(self, text="", fg=MUTED, bg=alpha(SECONDARY, 1.0), ring=BORDER,
                 font_size=FONT_CAPTION, height=36, icon=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.height = dp(height)
        self.padding = [dp(12), 0, dp(12), 0]
        self.spacing = dp(6)
        self.on_press = None
        self._fg = fg
        self._font_size = font_size
        self._radius = dp(height) / 2.0
        self._icon = None

        with self.canvas.before:
            self._fill_col = Color(*bg)
            self._fill = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[self._radius])
            self._ring_col = Color(*ring)
            self._ring = Line(rounded_rectangle=(0, 0, 0, 0, self._radius),
                              width=1.1)
        self.bind(pos=self._update, size=self._update)

        self._label = Label(text=text, color=fg, font_size=font_size,
                            size_hint=(None, None), valign="middle",
                            halign="left")
        self.bind(pos=self._layout, size=self._layout)
        self._label.bind(texture_size=self._layout)
        self.add_widget(self._label)
        self.set(text=text, fg=fg, bg=bg, ring=ring, icon=icon)

    def set(self, text=None, fg=None, bg=None, ring=None, icon=None,
            font_size=None):
        """Update pill content and colors; None keeps the current value."""
        if fg is not None:
            self._fg = fg
        if bg is not None:
            self._fill_col.rgba = bg
        if ring is not None:
            self._ring_col.rgba = ring
        if font_size is not None:
            self._font_size = font_size
        if icon is not None and icon is not self._icon:
            if self._icon is not None:
                self.remove_widget(self._icon)
            self._icon = icon
            self._icon.size_hint = (None, None)
            self.add_widget(self._icon)
        self._label.text = text if text is not None else self._label.text
        self._label.color = self._fg
        self._label.font_size = self._font_size
        self._layout()

    def _layout(self, *_):
        """Size the pill from its children and center them vertically."""
        width = self.padding[0] + self.padding[2]
        x = self.x + self.padding[0]
        if self._icon is not None:
            self._icon.x = x
            self._icon.y = self.y + (self.height - self._icon.height) / 2
            width += self._icon.width + self.spacing
            x += self._icon.width + self.spacing
        # Use the rendered text size (texture_size), not the label box size,
        # so icon-only pills stay compact
        label_w, label_h = self._label.texture_size
        self._label.size = (label_w, label_h)
        self._label.pos = (x, self.y + (self.height - label_h) / 2)
        width += label_w
        if self.width != width:
            self.width = width
        self._update()

    def _update(self, *_):
        self._fill.pos = self.pos
        self._fill.size = self.size
        self._ring.rounded_rectangle = (self.x, self.y, self.width, self.height,
                                        self._radius)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.on_press is not None:
                self.on_press()
            return True
        return super().on_touch_down(touch)


# ─────────────────────────────────────────────
# CENTERING HELPER — keeps fixed-height children centered in a row
# ─────────────────────────────────────────────
def keep_centered(widget):
    """Re-center a fixed-height widget inside its parent. BoxLayout pins
    size-hint-None children to the bottom on every layout, so this watches
    the child's own position and corrects it whenever the layout moves it."""

    def _recenter(*_):
        parent = widget.parent
        if parent is not None:
            target = parent.y + (parent.height - widget.height) / 2
            if abs(widget.y - target) > 0.5:
                widget.y = target

    widget.bind(pos=_recenter, size=_recenter)
    widget.bind(parent=lambda w, p: p.bind(size=_recenter) if p is not None else None)
    return widget


# ─────────────────────────────────────────────
# GLYPH — lucide-style battery icon with fill cells
# ─────────────────────────────────────────────
class BatteryGlyph(Widget):
    """Battery icon from the design: rounded shell, nub and fill cells.
    Cell count follows the reference (full > 60 %, medium > 20 %, low below)
    and the tint is mint when healthy, amber when low."""

    def __init__(self, pct=62, color=MINT, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(16), dp(16))
        self._pct = max(0, min(100, pct))
        with self.canvas:
            self._color = Color(*color)
            self._shell = Line(rounded_rectangle=(0, 0, 1, 1, dp(2)),
                               width=1.2)
            self._nub = RoundedRectangle(pos=(0, 0), size=(0, 0),
                                         radius=[dp(0.8)])
            self._cells = [
                RoundedRectangle(pos=(0, 0), size=(0, 0), radius=[dp(0.6)])
                for _ in range(3)
            ]
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def update(self, pct, color=None):
        self._pct = max(0, min(100, pct))
        if color is not None:
            self._color.rgba = color
        self._draw()

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

        # Shell: rounded rect (2,7)-(18,17); nub tab at the right
        self._shell.rounded_rectangle = (X(2), Y(7), 16 * scale, 10 * scale,
                                         2 * scale)
        self._nub.pos = (X(18), Y(11))
        self._nub.size = (3 * scale, 2 * scale)
        # Fill cells: short bars at x 5/9/13, y 11-13
        cells = 3 if self._pct > 60 else 2 if self._pct > 20 else 1
        for i, cell in enumerate(self._cells):
            if i < cells:
                cell.pos = (X(5 + i * 4), Y(11))
                cell.size = (2 * scale, 2 * scale)
            else:
                cell.size = (0, 0)


# ─────────────────────────────────────────────
# THRESHOLD SLIDER — slider drawn on the sensor scale
# ─────────────────────────────────────────────
# Inset (dp) of the slider track from its widget edges. The min/max scale
# labels are padded with the same value so they align with the track ends.
TRACK_INSET = 12
# Vertical motion (dp) past which a slider drag is handed back to the
# ScrollView so the page scrolls instead of the slider.
SCROLL_RELEASE_DISTANCE = 20


class ThresholdSlider(Widget):
    """Track + filled portion + thumb, tinted with the sensor tone.
    Values are snapped to `step`; assign `on_value_change` for updates."""

    def __init__(self, min_val=30.0, max_val=120.0, step=1.0, value=75.0,
                 tone=SKY, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(44)
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.step = float(step)
        self.tone = tone
        self.on_value_change = None
        self._value = float(value)
        self._dragging = False
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    # ── Value handling ──
    @property
    def value(self):
        return self._value

    def set_value(self, value, notify=False):
        snapped = self._snap(value)
        if snapped != self._value:
            self._value = snapped
            self._redraw()
            if notify and self.on_value_change:
                self.on_value_change(snapped)

    def _snap(self, value):
        value = max(self.min_val, min(self.max_val, float(value)))
        if self.step:
            value = round((value - self.min_val) / self.step) * self.step \
                + self.min_val
        return round(value, 4)

    # ── Geometry ──
    def _track_x(self):
        return self.x + dp(TRACK_INSET)

    def _track_w(self):
        return self.width - dp(TRACK_INSET) * 2

    def _thumb_x(self):
        pct = (self._value - self.min_val) / (self.max_val - self.min_val)
        return self._track_x() + pct * self._track_w()

    # ── Drawing ──
    def _redraw(self, *_):
        self.canvas.clear()
        track_h = dp(10)
        thumb_r = dp(11)
        ty = self.center_y - track_h / 2
        with self.canvas:
            # Track
            Color(*SECONDARY)
            RoundedRectangle(pos=(self._track_x(), ty),
                             size=(self._track_w(), track_h),
                             radius=[track_h / 2])
            # Filled portion up to the thumb
            fill_w = self._thumb_x() - self._track_x()
            if fill_w > 0:
                Color(*alpha(self.tone, 0.8))
                RoundedRectangle(pos=(self._track_x(), ty),
                                 size=(fill_w, track_h), radius=[track_h / 2])
            # Thumb
            cx, cty = self._thumb_x(), self.center_y
            Color(*self.tone)
            Ellipse(pos=(cx - thumb_r, cty - thumb_r),
                    size=(thumb_r * 2, thumb_r * 2))

    # ── Touch handling ──
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._dragging = True
            if not any(w() is self for w in touch.grab_list):
                touch.grab(self)
            self._update_from_touch(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._dragging:
            # Vertical drags scroll the page instead of moving the slider:
            # accumulate the vertical motion and release past a threshold
            ud = touch.ud
            ud['sv.dy'] = ud.get('sv.dy', 0.0) + abs(getattr(touch, 'dy', 0.0))
            if ud['sv.dy'] > dp(SCROLL_RELEASE_DISTANCE):
                self._dragging = False
                if any(w() is self for w in touch.grab_list):
                    touch.ungrab(self)
                ud.pop('sv.slider', None)
                return True
            self._update_from_touch(touch)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._dragging:
            self._dragging = False
            if any(w() is self for w in touch.grab_list):
                touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    # The page lives in a ScrollView, which grabs every touch and only
    # forwards it through on_scroll_* events. The AwarenessScrollView
    # forwards scroll-start events to sliders; grabbing the touch here
    # makes every drag move arrive at the slider, never at the page.
    # The value is applied on the first move so vertical drags (which
    # release back to the page) never change the threshold.
    def on_scroll_start(self, touch, check_children=True):
        if check_children and self.collide_point(*touch.pos):
            self._dragging = True
            if not any(w() is self for w in touch.grab_list):
                touch.grab(self)
            return True
        return False

    def on_scroll_move(self, touch, check_children=True):
        if self._dragging:
            self._update_from_touch(touch)
            return True
        return False

    def on_scroll_stop(self, touch, check_children=True):
        if self._dragging:
            self._dragging = False
            if any(w() is self for w in touch.grab_list):
                touch.ungrab(self)
            return True
        return False

    def _update_from_touch(self, touch):
        pct = max(0.0, min(1.0, (touch.x - self._track_x()) / self._track_w()))
        self.set_value(self.min_val + pct * (self.max_val - self.min_val),
                       notify=True)


# ─────────────────────────────────────────────
# SCROLL VIEW — forwards touches over threshold sliders
# ─────────────────────────────────────────────
class AwarenessScrollView(ScrollView):
    """ScrollView that hands touches landing on a ThresholdSlider to the
    slider itself: it captures the touch immediately (no scroll-timeout
    delay) and a drag on it never scrolls the page."""

    def on_scroll_start(self, touch, check_children=True):
        if check_children:
            touch.push()
            touch.apply_transform_2d(self.to_local)
            hit = self._forward_to_slider(touch)
            touch.pop()
            if hit:
                touch.ud['sv.slider'] = True
                return True
        return super().on_scroll_start(touch, check_children)

    def on_scroll_move(self, touch):
        if touch.ud.get('sv.slider'):
            # Mark the touch as a slider drag so the scroll-timeout click
            # simulation never fires mid-drag
            uid = self._get_uid()
            if uid in touch.ud:
                touch.ud[uid]['mode'] = 'slider'
            return True
        # A slider released the touch (vertical drag): allow scrolling again
        uid = self._get_uid()
        if uid in touch.ud and touch.ud[uid]['mode'] == 'slider':
            touch.ud[uid]['mode'] = 'unknown'
        return super().on_scroll_move(touch)

    def on_scroll_stop(self, touch, check_children=True):
        if touch.ud.get('sv.slider'):
            touch.ud.pop('sv.slider', None)
            return True
        return super().on_scroll_stop(touch, check_children)

    def _forward_to_slider(self, touch):
        """Walk the viewport subtree and let a slider under the touch handle
        the scroll-start event (which grabs the touch for the drag)."""
        def walk(widget):
            if isinstance(widget, ThresholdSlider) \
                    and widget.on_scroll_start(touch):
                return True
            for child in widget.children:
                if walk(child):
                    return True
            return False
        return walk(self._viewport)


# ─────────────────────────────────────────────
# TOOLTIP — small floating label shown on hover (desktop)
# ─────────────────────────────────────────────
class Tooltip(FloatLayout):
    """A small rounded label that follows the cursor. Use show()/hide()."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.opacity = 0
        with self.canvas.before:
            Color(*alpha(SURFACE, 0.98))
            self._bg = RoundedRectangle(pos=(0, 0), size=(0, 0),
                                        radius=[dp(8)])
            Color(*BORDER)
            self._ring = Line(rounded_rectangle=(0, 0, 0, 0, dp(8)), width=1)
        self._label = Label(text="", font_size=FONT_CAPTION, color=TEXT,
                            size_hint=(None, None), valign="middle",
                            halign="left")
        self.add_widget(self._label)
        self.bind(pos=self._update, size=self._update)
        self._update()

    def show(self, text, mx, my):
        """Show the tooltip near the cursor (clamped to the window)."""
        self._label.text = text
        tw, th = self._label.texture_size
        self.size = (tw + dp(20), th + dp(12))
        x = min(max(0.0, mx + dp(12)), Window.width - self.width)
        y = my + dp(16)
        if y + self.height > Window.height:
            y = my - self.height - dp(8)
        self.pos = (x, max(0.0, y))
        self.opacity = 1
        self._update()

    def hide(self):
        self.opacity = 0

    def _update(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._ring.rounded_rectangle = (self.x, self.y, self.width,
                                        self.height, dp(8))


# ─────────────────────────────────────────────
# EVENT ROW — one alert line in the recent/full logs
# ─────────────────────────────────────────────
class EventRow(BoxLayout):
    """Amber icon tile, 'X above threshold' description and a time label."""

    def __init__(self, sensor, event, when_text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(12)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))

        self.add_widget(keep_centered(IconTile(icon=sensor.icon, tone=AMBER,
                                               size=36, radius=RADIUS_ROW)))

        col = BoxLayout(orientation="vertical", spacing=dp(2))
        title = Label(text=f"{sensor.label} above threshold",
                      font_size=FONT_BODY, color=TEXT,
                      size_hint_y=None, halign="left", valign="middle")
        detail = Label(
            text=f"{format_value(sensor.id, event.value)} · threshold "
                 f"{format_value(sensor.id, event.threshold)}",
            font_size=FONT_CAPTION, color=MUTED,
            size_hint_y=None, halign="left", valign="middle",
        )
        col.add_widget(title)
        col.add_widget(detail)
        # Wrap text to the column width and grow the row with the content
        col.bind(size=lambda w, s: (
            setattr(title, "text_size", (s[0], None)),
            setattr(detail, "text_size", (s[0], None)),
        ))
        title.bind(texture_size=lambda w, s: setattr(w, "height", s[1]))
        detail.bind(texture_size=lambda w, s: setattr(w, "height", s[1]))
        self.add_widget(col)

        self.add_widget(keep_centered(autosize(Label(
            text=when_text, font_size=FONT_CAPTION, color=MUTED,
            size_hint=(None, None)))))


# ─────────────────────────────────────────────
# DIVIDER — thin hairline between list rows
# ─────────────────────────────────────────────
class Divider(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        with self.canvas:
            Color(*alpha(BORDER, 0.7))
            self._line = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, _: setattr(self._line, "pos", w.pos),
                  size=lambda w, s: setattr(self._line, "size", s))


# ─────────────────────────────────────────────
# MODAL — full-screen overlay with a bottom-sheet panel
# ─────────────────────────────────────────────
class Modal(FloatLayout):
    """Overlay with a bottom sheet: header bar on top, scrollable content
    below. Hidden until open(); subclasses fill the header and content."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._open = False
        self.opacity = 0

        # Backdrop
        with self.canvas.before:
            Color(*alpha(BG, 0.85))
            self._backdrop = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, s: setattr(self._backdrop, "pos", s),
                  size=lambda w, s: setattr(self._backdrop, "size", s))

        # Bottom sheet panel (rounded top corners, hairline border)
        self._panel = BoxLayout(orientation="vertical")
        self._panel.size_hint = (1, None)
        self._panel.height = min(Window.height * 0.85, dp(620))
        self._panel.pos_hint = {"x": 0, "y": 0}
        with self._panel.canvas.before:
            Color(*BORDER)
            self._panel_edge = RoundedRectangle(
                pos=(0, 0), size=(0, 0),
                radius=[(dp(26), dp(26)), (dp(26), dp(26)),
                        (dp(1), dp(1)), (dp(1), dp(1))])
            Color(*CARD)
            self._panel_fill = RoundedRectangle(
                pos=(0, 0), size=(0, 0),
                radius=[(dp(24), dp(24)), (dp(24), dp(24)), (0, 0), (0, 0)])
        self._panel.bind(pos=self._update_panel, size=self._update_panel)

        # Header bar (filled by subclasses)
        self._header = BoxLayout(orientation="horizontal", size_hint_y=None,
                                 height=dp(64), spacing=dp(12),
                                 padding=[dp(20), 0, dp(20), 0])
        self._panel.add_widget(self._header)

        # Scrollable content area (filled by subclasses)
        scroll = ScrollView()
        self._content = BoxLayout(orientation="vertical", size_hint_y=None)
        self._content.bind(minimum_height=self._content.setter("height"))
        scroll.add_widget(self._content)
        self._panel.add_widget(scroll)

        self.add_widget(self._panel)
        self._update_panel()

    def _update_panel(self, *_):
        x, y = self._panel.pos
        w, h = self._panel.size
        inset = dp(1.1)
        self._panel_edge.pos = (x - inset, y - inset)
        self._panel_edge.size = (w + inset * 2, h + inset * 2)
        self._panel_fill.pos = (x, y)
        self._panel_fill.size = (w, h)

    def open(self):
        self._open = True
        self.opacity = 1

    def close(self):
        self._open = False
        self.opacity = 0

    def on_touch_down(self, touch):
        if not self._open:
            return False
        # Consume touches on the backdrop so the page below cannot scroll
        if not self._panel.collide_point(*touch.pos):
            return True
        return super().on_touch_down(touch)
