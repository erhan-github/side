
import subprocess
import os

class NotificationService:
    """
    Sovereign Desktop Notification Layer.
    Uses macOS native AppleScript (osascript) to deliver Apple-grade alerts.
    """

    @staticmethod
    def _has_consent() -> bool:
        """Checks if the user has granted permission for notifications."""
        try:
            path = Path.cwd() / ".side" / "sovereign.json"
            if not path.exists():
                return False
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get("moat_pulse", {}).get("user_consent", False)
        except:
            return False

    @staticmethod
    def notify(title: str, subtitle: str, message: str, sound: Optional[str] = None):
        """
        Displays a structured macOS notification.
        - Checks for user_consent before firing.
        """
        if os.uname().sysname != "Darwin":
            return # Only run on macOS
            
        if not NotificationService._has_consent():
            return # Permission Denied

        # Escape double quotes
        m = message.replace('"', '\\"')
        t = title.replace('"', '\\"')
        s = subtitle.replace('"', '\\"')

        # Construct AppleScript
        script = f'display notification "{m}" with title "{t}" subtitle "{s}"'
        if sound:
            script += f' sound name "{sound}"'
        
        try:
            subprocess.run(["osascript", "-e", script], check=False)
        except Exception:
            pass

    def notify_violation(self, file_path: str, reason: str):
        """CRITICAL: Loud alert."""
        self.notify(
            title="🛑 [SOVEREIGN] INTERCEPTED",
            subtitle="Violation Detected",
            message=f"{os.path.basename(file_path)}: {reason}",
            sound="Basso"
        )

    def notify_drift(self, file_path: str):
        """ADVISORY: Silent alert."""
        self.notify(
            title="⚠️ [SIDE] DRIFT DETECTED",
            subtitle="Passive Shield Active",
            message=f"Observed change in {os.path.basename(file_path)}.",
            sound=None # SILENT
        )

    def notify_anchored(self, message: str):
        """Standard Anchor alert."""
        self.notify(
            title="⚓️ SOVEREIGN ANCHORED",
            subtitle="System of Record Updated",
            message=message,
            sound="Hero"
        )

# Singleton
notifier = NotificationService()
