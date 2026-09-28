from datetime import datetime, timedelta
from pathlib import Path
import sys, unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hid_defender.config import load_config
from hid_defender.models import SecurityEvent
from hid_defender.scoring import ScoringEngine

class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ScoringEngine(load_config(ROOT / "config/default_config.json"))
        cls.base = datetime.now().astimezone()

    def event(self, event_type, seconds=0, **details):
        return SecurityEvent(
            event_type=event_type, source="test",
            timestamp=(self.base + timedelta(seconds=seconds)).isoformat(),
            details=details
        )

    def test_normal(self):
        e = self.event("status")
        r = self.engine.evaluate([e], e)
        self.assertEqual((r.score, r.classification), (0, "normal"))

    def test_rapid_typing_is_suspicious(self):
        e = self.event("keystroke_burst", key_count=18,
                       mean_interval_seconds=0.045, coefficient_of_variation=0.18)
        r = self.engine.evaluate([e], e)
        self.assertEqual(r.classification, "suspicious")

    def test_hid_and_burst_is_attack(self):
        d = self.event("hid_device_connected", 0, is_keyboard=True)
        b = self.event("keystroke_burst", 1, key_count=24,
                       mean_interval_seconds=0.018, coefficient_of_variation=0.10)
        r = self.engine.evaluate([d,b], b)
        self.assertEqual(r.classification, "attack-related")

    def test_full_chain_caps_at_100(self):
        d = self.event("hid_device_connected", 0, is_keyboard=True)
        b = self.event("keystroke_burst", 1, key_count=30,
                       mean_interval_seconds=0.015, coefficient_of_variation=0.08)
        p = self.event("suspicious_process_started", 2, pid=12345, name="powershell.exe")
        r = self.engine.evaluate([d,b,p], p)
        self.assertEqual((r.score, r.classification), (100, "attack-related"))

if __name__ == "__main__":
    unittest.main()
