from threading import Event, Thread
from typing import Any, Callable
import os
import time
import psutil
from ..models import SecurityEvent

class ProcessMonitor:
    def __init__(self, config: dict[str, Any], callback: Callable[[SecurityEvent], None]) -> None:
        self.cfg = config["process"]
        self.callback = callback
        self.stop_event = Event()
        self.thread = None
        self.known_pids: set[int] = set()
        self.suspicious = {n.lower() for n in self.cfg["suspicious_names"]}

    def start(self) -> None:
        self.known_pids = set(psutil.pids())
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)

    def _run(self) -> None:
        while not self.stop_event.is_set():
            current = set(psutil.pids())
            for pid in current - self.known_pids:
                self._inspect(pid)
            self.known_pids = current
            time.sleep(float(self.cfg["poll_interval_seconds"]))

    def _inspect(self, pid: int) -> None:
        try:
            p = psutil.Process(pid)

            # Ignore processes created internally by this monitoring agent.
            # For example, the Windows HID monitor starts PowerShell to query devices.
            if p.ppid() == os.getpid():
                return

            name = p.name().lower()
            if name not in self.suspicious:
                return
            details = {"pid": pid, "name": name, "parent_pid": p.ppid()}
            try:
                parent = p.parent()
                details["parent_name"] = parent.name().lower() if parent else None
            except psutil.Error:
                details["parent_name"] = None
            if self.cfg.get("record_command_line", False):
                try:
                    details["command_line"] = p.cmdline()
                except psutil.Error:
                    details["command_line"] = []
            self.callback(SecurityEvent(
                event_type="suspicious_process_started",
                source="process_monitor",
                details=details
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return
