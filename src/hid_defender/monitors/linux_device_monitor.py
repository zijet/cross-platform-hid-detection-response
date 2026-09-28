from threading import Event, Thread
from typing import Any, Callable
import pyudev
from ..models import SecurityEvent

class LinuxHIDMonitor:
    def __init__(self, config: dict[str, Any], callback: Callable[[SecurityEvent], None]) -> None:
        self.callback = callback
        self.stop_event = Event()
        self.thread = None
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem="input")

    def start(self) -> None:
        self.monitor.start()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=3)

    def _run(self) -> None:
        while not self.stop_event.is_set():
            device = self.monitor.poll(timeout=1)
            if device is None or device.action != "add":
                continue
            props = device.properties
            if not (props.get("ID_INPUT_KEYBOARD") == "1" and props.get("ID_BUS") == "usb"):
                continue
            self.callback(SecurityEvent(
                event_type="hid_device_connected",
                source="linux_udev_keyboard_monitor",
                details={
                    "device_node": device.device_node,
                    "device_path": device.device_path,
                    "vendor_id": props.get("ID_VENDOR_ID"),
                    "model_id": props.get("ID_MODEL_ID"),
                    "name": props.get("ID_MODEL_FROM_DATABASE") or props.get("ID_MODEL") or "USB keyboard device",
                    "serial": props.get("ID_SERIAL_SHORT"),
                    "is_keyboard": True
                }
            ))
