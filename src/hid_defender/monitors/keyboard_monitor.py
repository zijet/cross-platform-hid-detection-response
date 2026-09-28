from collections import deque
from statistics import mean, pstdev
from time import monotonic
from typing import Any, Callable
from pynput import keyboard
from ..models import SecurityEvent

class KeystrokeTimingMonitor:
    """Records timing metadata only. Typed characters are never stored."""
    def __init__(self, config: dict[str, Any], callback: Callable[[SecurityEvent], None]) -> None:
        self.cfg = config["keystroke"]
        self.callback = callback
        self.timestamps: deque[float] = deque()
        self.listener = None
        self.last_emission = 0.0

    def start(self) -> None:
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def stop(self) -> None:
        if self.listener:
            self.listener.stop()

    def _on_press(self, _key) -> None:
        now = monotonic()
        window = float(self.cfg["analysis_window_seconds"])
        self.timestamps.append(now)
        while self.timestamps and now - self.timestamps[0] > window:
            self.timestamps.popleft()
        if len(self.timestamps) < int(self.cfg["minimum_keys"]):
            return
        intervals = [self.timestamps[i] - self.timestamps[i-1] for i in range(1, len(self.timestamps))]
        avg = mean(intervals)
        if avg >= float(self.cfg["burst_mean_interval_seconds"]):
            return
        if now - self.last_emission < float(self.cfg["burst_event_cooldown_seconds"]):
            return
        deviation = pstdev(intervals) if len(intervals) > 1 else 0.0
        cv = deviation / avg if avg > 0 else 0.0
        self.last_emission = now
        self.callback(SecurityEvent(
            event_type="keystroke_burst",
            source="keyboard_timing_monitor",
            details={
                "key_count": len(self.timestamps),
                "mean_interval_seconds": round(avg, 6),
                "coefficient_of_variation": round(cv, 6),
                "window_seconds": window,
                "content_recorded": False
            }
        ))
