# services/audio.py — Microphone capture and dB calculation
 
import pyaudio
import numpy as np
import threading
 
from ui.theme import CHUNK, RATE, CHANNELS, DB_MIN, DB_MAX
 
FORMAT = pyaudio.paInt16
 
 
def _rms_to_db(rms: float) -> float:
    """Convert linear RMS to dB, clamped to DB_MIN..DB_MAX."""
    if rms < 1e-6:
        return DB_MIN
    db = 20 * np.log10(rms / 32768.0) + 100  # offset so silence ≈ DB_MIN
    return float(np.clip(db, DB_MIN, DB_MAX))
 
 
class AudioMonitor:
    """
    Captures microphone input on a background daemon thread.
    Read .current_db from the main (Kivy) thread at any time.
    """
 
    def __init__(self):
        self.current_db: float = DB_MIN
        self._running  = False
        self._thread   = None
        self._pa       = None
        self._stream   = None
 
    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
 
    def stop(self):
        self._running = False
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._pa:
            self._pa.terminate()
 
    def _run(self):
        self._pa     = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        while self._running:
            try:
                data    = self._stream.read(CHUNK, exception_on_overflow=False)
                samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
                rms     = np.sqrt(np.mean(samples ** 2))
                self.current_db = _rms_to_db(rms)
            except Exception:
                pass