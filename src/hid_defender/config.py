from pathlib import Path
from typing import Any
import json

class ConfigError(RuntimeError):
    pass

def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"Configuration file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON configuration: {exc}") from exc
    required = ["correlation", "keystroke", "classification", "process", "responses", "logging"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ConfigError(f"Missing configuration sections: {', '.join(missing)}")
    return data
