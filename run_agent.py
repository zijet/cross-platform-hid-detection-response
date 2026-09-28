from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from hid_defender.app import DefenderApplication
from hid_defender.config import ConfigError, load_config

def main() -> int:
    try:
        config = load_config(ROOT / "config" / "default_config.json")
        DefenderApplication(config, ROOT).run()
        return 0
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 2
    except Exception as exc:
        print(f"Fatal error: {type(exc).__name__}: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
