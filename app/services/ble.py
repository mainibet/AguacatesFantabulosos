# app/services/ble.py — BLE connection + message parser.
#
# Two platform backends behind one BLEMonitor interface:
#   * macOS desktop  — bleak (CoreBluetooth via pyobjc)
#   * iOS (kivy-ios) — pyobjus + CoreBluetooth (bleak is not available there)
# The message parsers are shared; only the connection machinery differs.

import threading

try:
    from bleak import BleakScanner, BleakClient
    _BLEAK_AVAILABLE = True
except ImportError:
    _BLEAK_AVAILABLE = False

SERVICE_UUID     = "12345678-1234-5678-1234-567812345678"
CHAR_UUID        = "87654321-4321-8765-4321-876543214321"  # sound
CHAR_BAT_UUID    = "87654321-4321-8765-4321-876543214322"  # battery
CHAR_LIGHT_UUID  = "87654321-4321-8765-4321-876543214323"  # light
CHAR_CROWD_UUID  = "87654321-4321-8765-4321-876543214324"  # crowd
CHAR_CONFIG_UUID = "87654321-4321-8765-4321-876543214325"  # config (app→device)

DEVICE_NAME = "MyESP32C3_Sound"


# ─────────────────────────────────────────────
# SHARED PARSING — firmware message format:
#   SOUND:LOUD|Red|noise=38345  /  LIGHT:DARK|Green|RAW:8000
#   CROWD:LOW|Green|COUNT:0     /  BAT:85%|V:3.9
# ─────────────────────────────────────────────
class _Parser:

    def parse_sound(self, msg):
        # "SOUND:LOUD|Red|noise=38345"
        # Returns 0=quiet, 1=normal, 2=loud
        try:
            status = msg.split("SOUND:")[1].split("|")[0]
            return {"QUIET": 0, "NORMAL": 1, "LOUD": 2}.get(status, -1)
        except Exception:
            return None

    def parse_bat(self, msg):
        # "BAT:85%|V:3.9"
        try:
            return int(msg.split("BAT:")[1].split("%")[0])
        except Exception:
            return None

    def parse_light(self, msg):
        # "LIGHT:DARK|Green|RAW:8000"
        # Returns 0=dark, 1=normal, 2=bright
        try:
            status = msg.split("LIGHT:")[1].split("|")[0]
            return {"DARK": 0, "NORMAL": 1, "BRIGHT": 2}.get(status, -1)
        except Exception:
            return None

    def parse_crowd(self, msg):
        # "CROWD:LOW|Green|COUNT:0"
        # Returns 0=low, 1=moderate, 2=high
        try:
            status = msg.split("CROWD:")[1].split("|")[0]
            return {"LOW": 0, "MODERATE": 1, "HIGH": 2}.get(status, -1)
        except Exception:
            return None


# ─────────────────────────────────────────────
# MACOS BACKEND — bleak on a background thread
# ─────────────────────────────────────────────
if _BLEAK_AVAILABLE:
    import asyncio

    class BLEMonitor(_Parser):
        """bleak backend: the app polls `last_*` from its own tick loop;
        the scanner/connection runs on a daemon thread."""

        capable = True

        def __init__(self):
            self.connected  = False
            self.last_sound = None
            self.last_bat   = None
            self.last_light = None
            self.last_crowd = None
            self._running   = False
            self._thread    = None
            self._pending   = None   # target device found by the scanner
            self._pending_writes = []  # config payloads queued for the next connect
            self._write_lock = threading.Lock()

        def push_config(self, msg):
            """Queue a config write (e.g. 'noise=60;light=800') for the next
            connected window. Thread-safe; a no-op while disconnected."""
            with self._write_lock:
                self._pending_writes.append(msg)

        async def _drain_writes(self, client):
            """Write every queued config payload to the device."""
            with self._write_lock:
                pending, self._pending_writes = self._pending_writes, []
            for msg in pending:
                try:
                    await client.write_gatt_char(CHAR_CONFIG_UUID, msg.encode())
                except Exception as e:
                    print("Config write error:", e)

        def start(self):
            if not _BLEAK_AVAILABLE or self._thread is not None:
                return
            print("[BLE] backend: bleak (macOS)")
            self._running = True
            self._thread = threading.Thread(
                target=lambda: asyncio.run(self.run()),
                daemon=True
            )
            self._thread.start()

        def stop(self):
            """Stop the scan/connect loop and wait for the thread to finish,
            so the app can quit without crashing the interpreter."""
            self._running = False
            if self._thread is not None:
                self._thread.join(timeout=3.0)
                self._thread = None

        # ─────────────────────────────────────────────
        # SCANNER — wakes often so stop() returns quickly
        # ─────────────────────────────────────────────
        def _on_device(self, device, advertisement_data):
            name = advertisement_data.local_name or "" if advertisement_data else ""
            if name == DEVICE_NAME and self._pending is None:
                self._pending = device

        async def _find_device(self):
            """Scan until the wearable advertises; returns the device or None."""
            scanner = BleakScanner(detection_callback=self._on_device)
            await scanner.start()
            try:
                while self._running and self._pending is None:
                    await asyncio.sleep(0.5)
            finally:
                await scanner.stop()
            device, self._pending = self._pending, None
            return device

        async def run(self):
            while self._running:
                print("Scanning...")
                device = await self._find_device()
                if not device:
                    continue

                print("Found device, connecting...")
                try:
                    async with BleakClient(device) as client:
                        self.connected = True
                        print("BLE connected")

                        def on_sound(_, data):
                            msg = data.decode()
                            print("SOUND:", msg)
                            self.last_sound = msg

                        def on_bat(_, data):
                            msg = data.decode()
                            print("BAT:", msg)
                            self.last_bat = msg

                        def on_light(_, data):
                            msg = data.decode()
                            print("LIGHT:", msg)
                            self.last_light = msg

                        def on_crowd(_, data):
                            msg = data.decode()
                            print("CROWD:", msg)
                            self.last_crowd = msg

                        await client.start_notify(CHAR_UUID,       on_sound)
                        await client.start_notify(CHAR_BAT_UUID,   on_bat)
                        await client.start_notify(CHAR_LIGHT_UUID, on_light)
                        await client.start_notify(CHAR_CROWD_UUID, on_crowd)

                        while self._running:
                            await self._drain_writes(client)
                            await asyncio.sleep(1)

                except Exception as e:
                    print("Connection error:", e)
                    self.connected = False
                    await asyncio.sleep(2)


# ─────────────────────────────────────────────
# IOS BACKEND — CoreBluetooth via pyobjus
# Delegate callbacks arrive on the main thread (the manager runs on the
# main queue), so the app's _tick can read `last_*` directly. No threads.
# ─────────────────────────────────────────────
else:
    try:
        from pyobjus import autoclass, protocol
        from pyobjus.dylib_manager import load_framework
        # Same absolute path works on macOS (for testing) and iOS (system
        # framework). The kivy-ios Python bundles pyobjus 1.2.4.
        load_framework("/System/Library/Frameworks/CoreBluetooth.framework")
        _PYOBJUS_AVAILABLE = True
    except Exception:
        _PYOBJUS_AVAILABLE = False

    if _PYOBJUS_AVAILABLE:
        import ctypes

        _CBCentralManager = autoclass("CBCentralManager")
        _CBUUID   = autoclass("CBUUID")
        _NSArray  = autoclass("NSArray")
        _NSData   = autoclass("NSData")


        # CBManagerState (CoreBluetooth/CBManager.h)
        _STATE_POWERED_ON = 5
        # CBCharacteristicWriteType
        _WRITE_WITH_RESPONSE = 0

        def _prop(obj, name):
            """Read an ObjC property: pyobjus exposes some getters as
            ObjcMethod callables and others as already-converted values."""
            attr = getattr(obj, name)
            if type(attr).__name__ == "ObjcMethod" or callable(attr):
                try:
                    return attr()
                except TypeError:
                    return attr
            return attr


        class _CentralDelegate:
            def __init__(self, owner):
                self._owner = owner

            @protocol("CBCentralManagerDelegate")
            def centralManagerDidUpdateState_(self, manager):
                self._owner._on_state(_prop(manager, "state"))

            @protocol("CBCentralManagerDelegate")
            def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(
                    self, manager, peripheral, advertisementData, RSSI):
                self._owner._on_discovered(peripheral)

            @protocol("CBCentralManagerDelegate")
            def centralManager_didConnectPeripheral_(self, manager, peripheral):
                self._owner._on_connected(peripheral)

            @protocol("CBCentralManagerDelegate")
            def centralManager_didFailToConnectPeripheral_error_(
                    self, manager, peripheral, error):
                self._owner._log("connect failed: %r" % (error,))

            @protocol("CBCentralManagerDelegate")
            def centralManager_didDisconnectPeripheral_error_(
                    self, manager, peripheral, error):
                self._owner._on_disconnected()

        class _PeripheralDelegate:
            def __init__(self, owner):
                self._owner = owner

            @protocol("CBPeripheralDelegate")
            def peripheral_didDiscoverServices_(self, peripheral, error):
                self._owner._on_services(peripheral)

            @protocol("CBPeripheralDelegate")
            def peripheral_didDiscoverCharacteristicsForService_error_(
                    self, peripheral, service, error):
                self._owner._on_characteristics(service)

            @protocol("CBPeripheralDelegate")
            def peripheral_didUpdateValueForCharacteristic_error_(
                    self, peripheral, characteristic, error):
                self._owner._on_value(characteristic)

            @protocol("CBPeripheralDelegate")
            def peripheral_didWriteValueForCharacteristic_error_(
                    self, peripheral, characteristic, error):
                self._owner._log("config written to device")

            @protocol("CBPeripheralDelegate")
            def peripheral_didUpdateNotificationStateForCharacteristic_error_(
                    self, peripheral, characteristic, error):
                self._owner._log("notifications on %s" % (
                    self._owner._uuid_str(_prop(characteristic, "UUID")),))

        class BLEMonitor(_Parser):
            """CoreBluetooth backend via pyobjus (iOS)."""

            capable = True

            def __init__(self):
                self.connected  = False
                self.last_sound = None
                self.last_bat   = None
                self.last_light = None
                self.last_crowd = None
                self._running   = False
                self._central   = None
                self._central_delegate = None
                self._peripheral       = None
                self._peripheral_delegate = None
                self._chars = {}       # uuid string -> CBCharacteristic
                self._scanning = False
                self._pending_writes = []
                self._write_lock = threading.Lock()

            # ── lifecycle ──
            def start(self):
                if self._central is not None:
                    return
                self._running = True
                print("[BLE] backend: pyobjus/CoreBluetooth")
                self._central_delegate = _CentralDelegate(self)
                # queue=None -> callbacks on the main queue/thread
                self._central = _CBCentralManager.alloc().initWithDelegate_queue_(
                    self._central_delegate, None)
                self._log("central manager created")

            _STATE_NAMES = {0: "unknown", 1: "resetting", 2: "unsupported",
                            3: "unauthorized", 4: "poweredOff", 5: "poweredOn"}

            def _on_state(self, state):
                self._log("central state: %s (%s)" % (
                    state, self._STATE_NAMES.get(state, "?")))
                if state == _STATE_POWERED_ON:
                    self._start_scan()

            def stop(self):
                self._running = False
                if self._central is not None:
                    self._central.stopScan()
                    if self._peripheral is not None:
                        self._central.cancelPeripheralConnection_(self._peripheral)
                self._central = None
                self._central_delegate = None
                self._peripheral = None
                self._peripheral_delegate = None
                self._chars = {}
                self._scanning = False
                self.connected = False

            def _log(self, msg):
                print("[BLE] %s" % msg)

            # ── scan / connect ──
            def _on_state(self, state):
                self._log("central state: %s (%s)" % (
                    state, self._STATE_NAMES.get(state, "?")))
                if state == _STATE_POWERED_ON:
                    self._start_scan()

            def _start_scan(self):
                if not self._running or self._scanning or self._peripheral is not None:
                    return
                self._scanning = True
                services = _NSArray.arrayWithObject_(
                    _CBUUID.UUIDWithString_(SERVICE_UUID))
                self._central.scanForPeripheralsWithServices_options_(services, None)
                self._log("scanning for %s" % DEVICE_NAME)

            def _on_discovered(self, peripheral):
                if self._peripheral is not None:
                    return
                self._peripheral = peripheral
                self._central.stopScan()
                self._scanning = False
                self._central.connectPeripheral_options_(peripheral, None)
                self._log("connecting...")

            def _on_connected(self, peripheral):
                self._peripheral_delegate = _PeripheralDelegate(self)
                peripheral.setDelegate_(self._peripheral_delegate)
                services = _NSArray.arrayWithObject_(
                    _CBUUID.UUIDWithString_(SERVICE_UUID))
                peripheral.discoverServices_(services)
                self._log("connected, discovering services")

            def _on_disconnected(self):
                self.connected = False
                self._peripheral = None
                self._peripheral_delegate = None
                self._chars = {}
                self._log("disconnected")
                self._start_scan()  # the firmware re-advertises right away

            # ── characteristics ──
            def _on_services(self, peripheral):
                for service in self._iter(_prop(peripheral, "services")):
                    if self._uuid_str(_prop(service, "UUID")) == SERVICE_UUID:
                        peripheral.discoverCharacteristics_forService_(None, service)
                        return

            def _on_characteristics(self, service):
                for ch in self._iter(_prop(service, "characteristics")):
                    self._chars[self._uuid_str(_prop(ch, "UUID"))] = ch
                if (CHAR_UUID in self._chars and CHAR_BAT_UUID in self._chars
                        and CHAR_LIGHT_UUID in self._chars
                        and CHAR_CROWD_UUID in self._chars):
                    self._subscribe()
                    self.connected = True
                    self._log("connected, all characteristics found")
                    self._flush_writes()

            def _subscribe(self):
                per = self._peripheral
                per.setNotifyValue_forCharacteristic_(True, self._chars[CHAR_UUID])
                per.setNotifyValue_forCharacteristic_(True, self._chars[CHAR_BAT_UUID])
                per.setNotifyValue_forCharacteristic_(True, self._chars[CHAR_LIGHT_UUID])
                per.setNotifyValue_forCharacteristic_(True, self._chars[CHAR_CROWD_UUID])
                # The device notifies on threshold edges only; read the
                # current values once so the app has data immediately
                # (the characteristics are read-enabled on the firmware).
                per.readValueForCharacteristic_(self._chars[CHAR_UUID])
                per.readValueForCharacteristic_(self._chars[CHAR_BAT_UUID])
                per.readValueForCharacteristic_(self._chars[CHAR_LIGHT_UUID])
                per.readValueForCharacteristic_(self._chars[CHAR_CROWD_UUID])

            # ── data ──
            def _on_value(self, characteristic):
                msg = self._nsdata_to_str(_prop(characteristic, "value"))
                if msg is None:
                    return
                uuid = self._uuid_str(_prop(characteristic, "UUID"))
                if uuid == CHAR_UUID:
                    self.last_sound = msg
                elif uuid == CHAR_BAT_UUID:
                    self.last_bat = msg
                elif uuid == CHAR_LIGHT_UUID:
                    self.last_light = msg
                elif uuid == CHAR_CROWD_UUID:
                    self.last_crowd = msg

            # ── config writes (app → device thresholds) ──
            def push_config(self, msg):
                with self._write_lock:
                    self._pending_writes.append(msg)
                self._flush_writes()

            def _flush_writes(self):
                with self._write_lock:
                    pending, self._pending_writes = self._pending_writes, []
                if not pending:
                    return
                per = self._peripheral
                ch = self._chars.get(CHAR_CONFIG_UUID)
                if per is None or ch is None or not self.connected:
                    # not connected yet — try again once a connection lands
                    with self._write_lock:
                        self._pending_writes = pending + self._pending_writes
                    return
                for msg in pending:
                    buf = ctypes.create_string_buffer(msg.encode())
                    data = _NSData.dataWithBytes_length_(
                        ctypes.addressof(buf), len(msg.encode()))
                    per.writeValue_forCharacteristic_type_(
                        data, ch, _WRITE_WITH_RESPONSE)

            # ── helpers ──
            @staticmethod
            def _uuid_str(uuid):
                """CBUUID -> 'XXXXXXXX-...' string. pyobjus returns the
                NSString as an ObjcObject; UTF8String() yields the Python str."""
                s = _prop(uuid, "UUIDString")
                return s if isinstance(s, str) else s.UTF8String()

            @staticmethod
            def _iter(obj):
                """Iterate an ObjC NSArray, tolerating pyobjus auto-conversion
                to a Python list."""
                if obj is None:
                    return []
                if isinstance(obj, list):
                    return obj
                return [obj.objectAtIndex_(i) for i in range(_prop(obj, "count"))]

            @staticmethod
            def _nsdata_to_str(data):
                if data is None or _prop(data, "length") == 0:
                    return None
                length = _prop(data, "length")
                buf = ctypes.create_string_buffer(length)
                # pyobjus needs an explicit pointer address, not the buffer
                data.getBytes_length_(ctypes.addressof(buf), length)
                return buf.raw[:length].decode("utf-8", errors="replace")

    else:
        class BLEMonitor(_Parser):
            """No BLE backend available — demo-mode stub: stays disconnected,
            parsers still work for simulated data."""

            capable = False

            def __init__(self):
                self.connected  = False
                self.last_sound = None
                self.last_bat   = None
                self.last_light = None
                self.last_crowd = None

            def start(self):
                print("[BLE] backend: none (demo mode)")

            def stop(self):
                pass

            def push_config(self, msg):
                pass
