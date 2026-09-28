from datetime import datetime
from typing import Any, Iterable
from .models import DetectionResult, SecurityEvent

def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)

class ScoringEngine:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def evaluate(self, recent_events: Iterable[SecurityEvent], triggering_event: SecurityEvent) -> DetectionResult:
        events = list(recent_events)
        score = 0
        indicators: list[str] = []
        device_events = [e for e in events if e.event_type == "hid_device_connected"]
        burst_events = [e for e in events if e.event_type == "keystroke_burst"]
        process_events = [e for e in events if e.event_type == "suspicious_process_started"]
        latest_device = device_events[-1] if device_events else None
        latest_burst = burst_events[-1] if burst_events else None
        latest_process = process_events[-1] if process_events else None

        if latest_device:
            score += 20
            indicators.append("New HID device detected (+20)")
            if latest_device.details.get("is_keyboard", True):
                score += 10
                indicators.append("Keyboard-class HID (+10)")

        if latest_burst:
            avg = float(latest_burst.details.get("mean_interval_seconds", 1.0))
            cv = float(latest_burst.details.get("coefficient_of_variation", 1.0))
            count = int(latest_burst.details.get("key_count", 0))
            k = self.config["keystroke"]
            if avg < k["very_fast_interval_seconds"]:
                score += 35; indicators.append("Extremely fast keystrokes (+35)")
            elif avg < k["fast_interval_seconds"]:
                score += 30; indicators.append("Very fast keystrokes (+30)")
            elif avg < k["moderate_interval_seconds"]:
                score += 20; indicators.append("Fast keystrokes (+20)")
            else:
                score += 10; indicators.append("Abnormal keystroke burst (+10)")
            if cv < k["low_variability_cv"]:
                score += 15; indicators.append("Low timing variability (+15)")
            if count >= 20:
                score += 10; indicators.append("Large keystroke burst (+10)")

        if latest_process:
            score += 30
            indicators.append(f"Relevant process created: {latest_process.details.get('name', 'unknown')} (+30)")

        if latest_device and latest_burst:
            delta = (_parse_time(latest_burst.timestamp) - _parse_time(latest_device.timestamp)).total_seconds()
            if 0 <= delta <= self.config["correlation"]["window_seconds"]:
                score += 10; indicators.append("HID followed by rapid input (+10)")

        if latest_burst and latest_process:
            delta = (_parse_time(latest_process.timestamp) - _parse_time(latest_burst.timestamp)).total_seconds()
            if 0 <= delta <= self.config["correlation"]["process_after_burst_seconds"]:
                score += 15; indicators.append("Rapid input followed by process (+15)")

        score = min(score, 100)
        c = self.config["classification"]
        classification = "attack-related" if score >= c["attack_threshold"] else "suspicious" if score >= c["suspicious_threshold"] else "normal"
        return DetectionResult(
            score=score, classification=classification,
            indicators=indicators or ["No suspicious indicator"],
            triggering_event_id=triggering_event.event_id,
            triggering_event_type=triggering_event.event_type
        )
