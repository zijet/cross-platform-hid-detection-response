from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any
import platform
import uuid


def local_now_iso() -> str:
    """Return the current OS-local time with its UTC offset."""
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


@dataclass(slots=True)
class SecurityEvent:
    event_type: str
    source: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=local_now_iso)
    platform: str = field(default_factory=platform.system)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DetectionResult:
    score: int
    classification: str
    indicators: list[str]
    triggering_event_id: str
    triggering_event_type: str
    timestamp: str = field(default_factory=local_now_iso)
    action_taken: str = "logged"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
