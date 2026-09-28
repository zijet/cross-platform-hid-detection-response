from threading import Event, Thread
from typing import Any, Callable
import json, subprocess, time
from ..models import SecurityEvent

class WindowsHIDMonitor:
    def __init__(self, config: dict[str, Any], callback: Callable[[SecurityEvent], None]) -> None:
        self.cfg = config["device"]
        self.callback = callback
        self.stop_event = Event()
        self.thread = None
        self.known_ids: set[str] = set()

    def start(self) -> None:
        self.known_ids = set(self._snapshot())
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=3)

    def _run(self) -> None:
        while not self.stop_event.is_set():
            snapshot = self._snapshot()
            current = set(snapshot)
            for instance_id in current - self.known_ids:
                row = snapshot[instance_id]
                self.callback(SecurityEvent(
                    event_type="hid_device_connected",
                    source="windows_pnp_keyboard_monitor",
                    details={
                        "instance_id": instance_id,
                        "name": row.get("FriendlyName") or row.get("Description") or "Keyboard device",
                        "status": row.get("Status"),
                        "is_keyboard": True
                    }
                ))
            self.known_ids = current
            time.sleep(float(self.cfg["poll_interval_seconds"]))

    @staticmethod
    def _snapshot() -> dict[str, dict[str, Any]]:
        commands = [
            "Get-PnpDevice -Class Keyboard -PresentOnly | Select-Object InstanceId,FriendlyName,Status | ConvertTo-Json -Compress",
            "Get-CimInstance Win32_Keyboard | Select-Object PNPDeviceID,Description,Status | ConvertTo-Json -Compress"
        ]
        for command in commands:
            try:
                cp = subprocess.run(
                    ["powershell","-NoProfile","-Command",command],
                    capture_output=True, text=True, timeout=10, check=False
                )
                if cp.returncode != 0 or not cp.stdout.strip():
                    continue
                data = json.loads(cp.stdout)
                rows = data if isinstance(data, list) else [data]
                result = {}
                for row in rows:
                    instance_id = row.get("InstanceId") or row.get("PNPDeviceID")
                    if instance_id:
                        result[str(instance_id)] = row
                return result
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
                continue
        return {}
