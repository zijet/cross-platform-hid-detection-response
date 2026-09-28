from typing import Any
import platform, subprocess, threading
import psutil
from .models import DetectionResult, SecurityEvent

class Responder:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def respond(self, result: DetectionResult, event: SecurityEvent) -> str:
        actions = ["logged"]
        if result.classification in {"suspicious", "attack-related"}:
            self._console_alert(result)
            actions.append("console alert")
            if self.config["responses"].get("desktop_notifications", True):
                threading.Thread(target=self._desktop_alert, args=(result,), daemon=True).start()
                actions.append("desktop alert requested")

        r = self.config["responses"]
        if r.get("terminate_process", False) and result.score >= r["termination_threshold"] and event.event_type == "suspicious_process_started":
            if self._terminate_allowlisted(event):
                actions.append("allowlisted test process terminated")

        if r.get("lock_session", False) and result.score >= r["lock_threshold"] and self._lock_session():
            actions.append("session lock requested")
        return ", ".join(actions)

    @staticmethod
    def _console_alert(result: DetectionResult) -> None:
        print("\n" + "=" * 68)
        print(f"SECURITY ALERT: {result.classification.upper()} | SCORE {result.score}/100")
        for item in result.indicators:
            print(f" - {item}")
        print("=" * 68 + "\n")

    @staticmethod
    def _desktop_alert(result: DetectionResult) -> None:
        title = "USB/HID Security Alert"
        message = f"{result.classification.upper()} activity detected. Score: {result.score}/100"
        try:
            if platform.system() == "Windows":
                command = (
                    "Add-Type -AssemblyName PresentationFramework; "
                    f"[System.Windows.MessageBox]::Show('{message}','{title}') | Out-Null"
                )
                subprocess.Popen(["powershell","-NoProfile","-Command",command],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif platform.system() == "Linux":
                subprocess.Popen(["notify-send", title, message],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            return

    def _terminate_allowlisted(self, event: SecurityEvent) -> bool:
        pid = event.details.get("pid")
        name = str(event.details.get("name", "")).lower()
        allowed = {n.lower() for n in self.config["responses"]["termination_allowlist"]}
        if not isinstance(pid, int) or name not in allowed:
            return False
        try:
            process = psutil.Process(pid)
            if process.name().lower() != name:
                return False
            process.terminate()
            process.wait(timeout=3)
            return True
        except psutil.Error:
            return False

    @staticmethod
    def _lock_session() -> bool:
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["rundll32.exe","user32.dll,LockWorkStation"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            if platform.system() == "Linux":
                for command in (["loginctl","lock-session"], ["gnome-screensaver-command","-l"]):
                    try:
                        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return True
                    except FileNotFoundError:
                        pass
        except OSError:
            pass
        return False
