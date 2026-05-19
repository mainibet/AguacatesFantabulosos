from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.metrics import dp
from ui.theme import TEXT, MUTED, GOOD, WARN, DANGER, LIGHT_COLOR
from ui.widgets import Card


def _batt_color(pct):
    if pct > 50: return GOOD
    if pct > 20: return WARN
    return DANGER


class BatteryCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(72)
        self.orientation = 'horizontal'
        self.spacing = dp(12)

        self._icon = Label(text="🔋", font_size='16sp',
                           font_name='Emoji',#for MacOs
                           size_hint=(None, 1), width=dp(24))
        self.add_widget(self._icon)

        info = BoxLayout(orientation='vertical', spacing=dp(2))
        self._pct_lbl  = Label(text="72%", font_size='18sp', bold=True,
                                color=TEXT, halign='right', valign='middle')
        self._pct_lbl.bind(size=lambda w,s: setattr(w,'text_size',s))
        self._status   = Label(text="Good", font_size='11sp',
                                color=GOOD, halign='left', valign='middle')
        self._status.bind(size=lambda w,s: setattr(w,'text_size',s))
        info.add_widget(self._pct_lbl)
        info.add_widget(self._status)
        self.add_widget(info)

    def update(self, pct):
        color = _batt_color(pct)
        self._pct_lbl.text = f"{pct}%"
        self._icon.text    = "🔋" if pct > 50 else "🪫" if pct > 20 else "⚠️"
        if pct > 50:
            self._status.text  = "Good"
        elif pct > 20:
            self._status.text  = "Charge soon"
        else:
            self._status.text  = "Low — charge now"
        self._status.color = color


class SensorMiniCard(Card):
    """Small card: title + value + unit + status."""

    def __init__(self, title, unit, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(90)
        self._unit = unit

        self.add_widget(Label(text=title, font_size='10sp', color=(1,1,1,0.5),
                              size_hint_y=None, height=dp(16),
                              halign='left', valign='middle'))

        self._val_lbl = Label(text=f"--{unit}", font_size='20sp', bold=True,
                              color=TEXT, size_hint_y=None, height=dp(32),
                              halign='left', valign='middle')
        self._val_lbl.bind(size=lambda w,s: setattr(w,'text_size',s))
        self.add_widget(self._val_lbl)

        self._status = Label(text="—", font_size='11sp', color=(1,1,1,0.5),
                             size_hint_y=None, height=dp(20),
                             halign='left', valign='middle')
        self._status.bind(size=lambda w,s: setattr(w,'text_size',s))
        self.add_widget(self._status)

    def update(self, value, threshold):
        self._val_lbl.text = f"{value}{self._unit}"
        exceeded = value > threshold
        near     = value > threshold * 0.85
        if exceeded:
            self._status.text  = "⚠ Above threshold"
            self._status.color = DANGER
        elif near:
            self._status.text  = "Near threshold"
            self._status.color = WARN
        else:
            self._status.text  = "Normal"
            self._status.color = GOOD