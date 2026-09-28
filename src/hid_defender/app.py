from collections import deque
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from typing import Any
import platform, signal
from .logger import StructuredLogger
from .models import SecurityEvent
from .responders import Responder
from .scoring import ScoringEngine
from .monitors.keyboard_monitor import KeystrokeTimingMonitor
from .monitors.process_monitor import ProcessMonitor

class DefenderApplication:
    def __init__(self, config: dict[str, Any], project_root: Path) -> None:
        self.config = config
        self.queue: Queue[SecurityEvent] = Queue()
        self.events: deque[SecurityEvent] = deque()
        self.logger = StructuredLogger(config, project_root)
        self.scoring = ScoringEngine(config)
        self.responder = Responder(config)
        self.monitors = []
        self.running = True

    def _callback(self, event: SecurityEvent) -> None:
        self.queue.put(event)

    def _build_monitors(self) -> None:
        self.monitors = [
            KeystrokeTimingMonitor(self.config, self._callback),
            ProcessMonitor(self.config, self._callback)
        ]
        system = platform.system()
        if system == "Windows":
            from .monitors.windows_device_monitor import WindowsHIDMonitor
            self.monitors.append(WindowsHIDMonitor(self.config, self._callback))
        elif system == "Linux":
            from .monitors.linux_device_monitor import LinuxHIDMonitor
            self.monitors.append(LinuxHIDMonitor(self.config, self._callback))
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

    def run(self) -> None:
        self._build_monitors()
        signal.signal(signal.SIGINT, self._handle_signal)
        for monitor in self.monitors:
            monitor.start()
        print("USB/HID Defender v0.1 is running.")
        print("Timing metadata only; typed characters are not recorded.")
        print("Press Ctrl+C to stop.\n")
        try:
            while self.running:
                try:
                    event = self.queue.get(timeout=0.5)
                except Empty:
                    continue
                self._process(event)
        finally:
            for monitor in reversed(self.monitors):
                monitor.stop()
            print("Agent stopped safely.")

    def _process(self, event: SecurityEvent) -> None:
        self.logger.log_event(event)
        self.events.append(event)
        self._prune()
        result = self.scoring.evaluate(self.events, event)
        result.action_taken = self.responder.respond(result, event)
        self.logger.log_detection(result)
        print(f"[{event.timestamp}] {event.event_type} -> {result.classification} ({result.score}/100)")

    def _prune(self) -> None:
        now = datetime.now().astimezone()
        cutoff = float(self.config["correlation"]["window_seconds"])
        while self.events:
            oldest = datetime.fromisoformat(self.events[0].timestamp)
            if (now - oldest).total_seconds() <= cutoff:
                break
            self.events.popleft()

    def _handle_signal(self, _signum, _frame) -> None:
        self.running = False
