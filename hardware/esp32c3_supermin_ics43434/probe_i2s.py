# Lab diagnostic for ICS-43434 on ESP32-C3 (run with mpremote)
# Usage: mpremote connect <port> run probe_i2s.py
# Wiring under test: WS(LRCK)->GPIO4, SCK(BCLK)->GPIO5, SD->GPIO10 (or GPIO6)
from machine import I2S, Pin
import struct, time, machine

GPIO_IN = 0x6000403C
SD_PIN = 10          # change to 6 if SD is back on GPIO6

def capture(sd, pull=None):
    p = Pin(sd, Pin.IN, pull) if pull else Pin(sd, Pin.IN)
    a = I2S(
        0, sck=Pin(5), ws=Pin(4), sd=Pin(sd),
        mode=I2S.RX, bits=32, format=I2S.STEREO, rate=16000, ibuf=16384,
    )
    time.sleep_ms(150)
    BUF = bytearray(8192)
    n = a.readinto(BUF)
    nframes = n // 8
    best = (0, 0, 0, 0)  # (min, max, amp, nonm1) of the louder slot
    for off, slot in ((0, "L"), (4, "R")):
        mn = 0x7FFFFFFF
        mx = -0x80000000
        wm1 = 0
        for i in range(nframes):
            w = struct.unpack_from("<i", BUF, i * 8 + off)[0]
            if w == -1:
                wm1 += 1
            else:
                v = w >> 8  # 24-bit data left-justified in 32-bit frame
                if v < mn: mn = v
                if v > mx: mx = v
        nonm1 = nframes - wm1
        if nonm1 and (nonm1, mx - mn) > (best[3], best[2]):
            best = (mn, mx, mx - mn, nonm1)
    a.deinit()
    time.sleep_ms(50)
    if best[3] == 0:
        return None, None, 0, 0
    return best

print("=== 1) CLOCK CHECK (WS=G4, SCK=G5 should toggle) ===")
a = I2S(0, sck=Pin(5), ws=Pin(4), sd=Pin(SD_PIN),
        mode=I2S.RX, bits=32, format=I2S.STEREO, rate=16000, ibuf=16384)
time.sleep_ms(100)
c4 = c5 = 0
l4 = l5 = None
t0 = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), t0) < 100:
    v = machine.mem32[GPIO_IN]
    b4, b5 = (v >> 4) & 1, (v >> 5) & 1
    if l4 is not None and b4 != l4: c4 += 1
    if l5 is not None and b5 != l5: c5 += 1
    l4, l5 = b4, b5
print("  WS transitions=%d, SCK transitions=%d (both >0 = clocks alive)" % (c4, c5))
a.deinit()

print("=== 2) CAPTURE on GPIO%d (music playing should give varying samples) ===" % SD_PIN)
for t in range(3):
    mn, mx, amp, nonm1 = capture(SD_PIN)
    if nonm1:
        print("  trial%d: min=%d max=%d amplitude=%d non-m1-frames=%d" % (t, mn, mx, amp, nonm1))
    else:
        print("  trial%d: NO DATA (all words constant)" % t)

print("=== 3) PULL TEST (floating pin follows pulls = mic NOT driving) ===")
mn, mx, amp, nonm1 = capture(SD_PIN, Pin.PULL_DOWN)
print("  PULL_DOWN: %s" % ("min=%d max=%d amplitude=%d" % (mn, mx, amp) if nonm1 else "NO DATA"))
mn, mx, amp, nonm1 = capture(SD_PIN, Pin.PULL_UP)
print("  PULL_UP:   %s" % ("min=%d max=%d amplitude=%d" % (mn, mx, amp) if nonm1 else "NO DATA"))

print("""
=== VERDICT ===
- amplitude > 0 in step 2 AND pulls don't change step 3  -> MIC WORKS
- amplitude == 0 and pulls flip the reading (PD->zeros, PU->-1)
  -> pin FLOATS: mic SD not electrically connected / not powered
- clocks == 0 in step 1 -> I2S peripheral not running
""")
