from datetime import datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from hid_defender.config import load_config
from hid_defender.models import SecurityEvent
from hid_defender.scoring import ScoringEngine

def make(base, seconds, event_type, **details):
    return SecurityEvent(
        event_type=event_type,
        source="simulator",
        timestamp=(base + timedelta(seconds=seconds)).isoformat(),
        details=details
    )

def main():
    engine = ScoringEngine(load_config(ROOT / "config/default_config.json"))
    base = datetime.now().astimezone()
    scenarios = [
        ("1 Normal activity", [make(base,0,"status",note="agent operational")]),
        ("2 Rapid harmless text", [
            make(base,0,"keystroke_burst",key_count=18,mean_interval_seconds=0.045,coefficient_of_variation=0.18)
        ]),
        ("3 New HID plus rapid text", [
            make(base,0,"hid_device_connected",name="Arduino Leonardo",is_keyboard=True),
            make(base,1,"keystroke_burst",key_count=24,mean_interval_seconds=0.018,coefficient_of_variation=0.10)
        ]),
        ("4 New HID, rapid text and shell", [
            make(base,0,"hid_device_connected",name="Arduino Leonardo",is_keyboard=True),
            make(base,1,"keystroke_burst",key_count=30,mean_interval_seconds=0.015,coefficient_of_variation=0.08),
            make(base,2,"suspicious_process_started",pid=12345,name="powershell.exe",parent_name="explorer.exe")
        ])
    ]
    for title, events in scenarios:
        print(f"\nScenario {title}")
        recent = []
        for event in events:
            recent.append(event)
            result = engine.evaluate(recent, event)
            print(f"{event.event_type:30} score={result.score:3} class={result.classification}")
        for indicator in result.indicators:
            print(f" - {indicator}")

if __name__ == "__main__":
    main()
