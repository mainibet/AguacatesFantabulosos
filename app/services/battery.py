import platform

class BatteryMonitor:
    """Read the battery level of the device running the app (not the BLE sensor)."""

    def get(self):
        """Returns dict with percent(int) and charging(bool). Never throws."""
        try:
            return self._read()
        except Exception:
            return {"percent": -1, "charging": False}

    def _read(self):
        system = platform.system()

        if system == "Linux":
            return self._linux()
        elif system == "Darwin":
            return self._macos()
        elif system == "Windows":
            return self._windows()
        else:
            # Android (Kivy) — usar plyer si está disponible
            return self._plyer()

    def _linux(self):
        import pathlib
        base = pathlib.Path("/sys/class/power_supply")
        for bat in base.glob("BAT*"):
            cap  = (bat / "capacity").read_text().strip()
            stat = (bat / "status").read_text().strip()
            return {"percent": int(cap), "charging": stat == "Charging"}
        return {"percent": -1, "charging": False}

    def _macos(self):
        import subprocess, json
        out = subprocess.check_output(
            ["pmset", "-g", "batt"], text=True
        )
        # "Now drawing from 'Battery Power'; 72%; discharging"
        for line in out.splitlines():
            if "%" in line:
                pct      = int(line.split("%")[0].split()[-1])
                charging = "charging" in line.lower() or "AC" in line
                return {"percent": pct, "charging": charging}
        return {"percent": -1, "charging": False}

    def _windows(self):
        import psutil
        b = psutil.sensors_battery()
        if b:
            return {"percent": int(b.percent), "charging": b.power_plugged}
        return {"percent": -1, "charging": False}

    def _plyer(self):
        try:
            from plyer import battery
            status = battery.status
            return {
                "percent":  int(status.get("percentage", -1)),
                "charging": status.get("isCharging", False),
            }
        except Exception:
            return {"percent": -1, "charging": False}