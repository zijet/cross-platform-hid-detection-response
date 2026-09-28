from pathlib import Path
from threading import Lock
from typing import Any
import csv, json
from .models import DetectionResult, SecurityEvent

class StructuredLogger:
    CSV_FIELDS = ["timestamp","score","classification","triggering_event_type","triggering_event_id","indicators","action_taken"]

    def __init__(self, config: dict[str, Any], project_root: Path) -> None:
        cfg = config["logging"]
        self.directory = project_root / cfg["directory"]
        self.directory.mkdir(parents=True, exist_ok=True)
        self.raw_path = self.directory / cfg["raw_events_jsonl"]
        self.detection_path = self.directory / cfg["detections_jsonl"]
        self.csv_path = self.directory / cfg["detections_csv"]
        self.lock = Lock()
        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=self.CSV_FIELDS).writeheader()

    def log_event(self, event: SecurityEvent) -> None:
        self._append_jsonl(self.raw_path, event.to_dict())

    def log_detection(self, result: DetectionResult) -> None:
        self._append_jsonl(self.detection_path, result.to_dict())
        row = {
            "timestamp": result.timestamp,
            "score": result.score,
            "classification": result.classification,
            "triggering_event_type": result.triggering_event_type,
            "triggering_event_id": result.triggering_event_id,
            "indicators": " | ".join(result.indicators),
            "action_taken": result.action_taken,
        }
        with self.lock:
            with self.csv_path.open("a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=self.CSV_FIELDS).writerow(row)

    def _append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        with self.lock:
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
