from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from ui.theme import TEXT, GOOD, WARN, DANGER


def _batt_color(pct):
    if pct > 50: 
        return GOOD
    if pct > 20: 
        return WARN
    return DANGER


class BatteryCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(72)
        self.padding = dp(4)

        # Contenedor interno que simula el recuadro estético
        inner = BoxLayout(
            orientation='horizontal', 
            spacing=dp(10),
            padding=[dp(12), dp(8), dp(12), dp(8)]
        )

        # Dibujamos el recuadro de fondo (Card) en el canvas del contenedor interno
        with inner.canvas.before:
            Color(0.118, 0.133, 0.161, 1)  # Color gris oscuro de la tarjeta
            self._bg_rect = RoundedRectangle(pos=inner.pos, size=inner.size, radius=[dp(8)])
        
        # Vincular cambios de tamaño/posición para que el fondo se adapte de forma dinámica
        inner.bind(pos=self._update_rect, size=self._update_rect)

        # Icono con el tamaño de fuente original (16sp)
        self._icon = Label(
            text="🔋", font_size='16sp', font_name='Emoji',
            size_hint=(None, 1), width=dp(28),
            halign='center', valign='middle'
        )
        self._icon.bind(size=lambda w, s: setattr(w, 'text_size', s))

        info = BoxLayout(orientation='vertical', spacing=dp(2))

        self._pct_lbl = Label(
            text="-- %", font_size='16sp', bold=True,
            color=TEXT, halign='left', valign='middle'
        )
        self._pct_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))

        self._status = Label(
            text="Reading...", font_size='12sp',
            color=GOOD, halign='left', valign='middle'
        )
        self._status.bind(size=lambda w, s: setattr(w, 'text_size', s))

        info.add_widget(self._pct_lbl)
        info.add_widget(self._status)
        inner.add_widget(self._icon)
        inner.add_widget(info)
        self.add_widget(inner)

    def _update_rect(self, instance, value):
        """Mantiene el fondo alineado con las dimensiones del contenedor"""
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size

    def update(self, pct):
        if pct < 0:
            self._pct_lbl.text = "N/A"
            self._status.text = "No data"
            self._status.color = WARN
            return

        color = _batt_color(pct)
        self._pct_lbl.text = f"{pct:.0f}%"
        self._status.color = color

        # Control dinámico de emojis y estados sin operadores ternarios
        if pct > 50:
            self._icon.text = "🔋"
            self._status.text = "Good"
        else:
            if pct > 20:
                self._icon.text = "🪫"
                self._status.text = "Charge soon"
            else:
                self._icon.text = "⚠️"
                self._status.text = "Low — charge now"


# Diccionarios de estados para mapeo limpio
LIGHT_LABELS = {
    0: ("🌑", "Dark", GOOD),
    1: ("🌤", "Normal", WARN),
    2: ("☀️", "Bright", DANGER),
}

CROWD_LABELS = {
    'low': ("🟢", "Quiet", GOOD),
    'medium': ("🟡", "Moderate", WARN),
    'high': ("🔴", "Crowded", DANGER),
}


class SensorMiniCard(BoxLayout):
    def __init__(self, title, mode='number', unit='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(100)
        self.padding = dp(8)
        self._mode = mode
        self._unit = unit

        # Añadimos un fondo estético individual a cada mini tarjeta de sensor
        with self.canvas.before:
            Color(0.118, 0.133, 0.161, 1)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update_rect, size=self._update_rect)

        self._title_lbl = Label(
            text=title, font_size='10sp', color=(1, 1, 1, 0.5),
            size_hint_y=None, height=dp(16),
            halign='left', valign='middle'
        )
        self._title_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))

        self._val_lbl = Label(
            text="--", font_size='18sp', bold=True,
            color=TEXT, size_hint_y=None, height=dp(30),
            halign='left', valign='middle', font_name='Emoji'
        )
        self._val_lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))

        self._status = Label(
            text="—", font_size='13sp', color=(1, 1, 1, 0.5),
            size_hint_y=None, height=dp(22),
            halign='left', valign='middle'
        )
        self._status.bind(size=lambda w, s: setattr(w, 'text_size', s))

        self.add_widget(self._title_lbl)
        self.add_widget(self._val_lbl)
        self.add_widget(self._status)

    def _update_rect(self, instance, value):
        self._bg_rect.pos = instance.pos
        self._bg_rect.size = instance.size

    def update(self, value, threshold=None, mode=None):
        if value is None:
            self._val_lbl.text = "--"
            self._status.text = "—"
            return

        m = mode
        if m is None:
            m = self._mode

        if m == 'light':
            icon, label, color = LIGHT_LABELS.get(int(value), ("?", "Unknown", WARN))
            self._val_lbl.text = f"{icon}  {label}"
            if value >= 2:
                self._status.text = "Too bright"
                self._status.color = DANGER
            else:
                self._status.text = "OK"
                self._status.color = GOOD

        else:
            if m == 'crowd':
                pct = float(value)
                if pct < 40:
                    key = 'low'
                else:
                    if pct < 70:
                        key = 'medium'
                    else:
                        key = 'high'
                icon, label, color = CROWD_LABELS[key]
                self._val_lbl.text = f"{icon}  {label}"
                self._status.text = f"{pct:.0f}%"
                self._status.color = color

            else:  # Modo numérico estándar
                self._val_lbl.text = f"{value:.0f}{self._unit}"
                
                # Determinación de alertas sin ternarios
                exceeded = False
                near = False
                if threshold:
                    if value > threshold:
                        exceeded = True
                    if value > (threshold * 0.85):
                        near = True

                if exceeded:
                    self._status.text = "⚠ Alert"
                    self._status.color = DANGER
                else:
                    if near:
                        self._status.text = "Near limit"
                        self._status.color = WARN
                    else:
                        self._status.text = "Normal"
                        self._status.color = GOOD