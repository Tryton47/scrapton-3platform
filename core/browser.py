"""
Playwright-based stealth browser manager with session/cookie persistence.
"""
import json
from pathlib import Path
from typing import Any
from config.settings import settings

DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

class BrowserManager:
    """Manages browser lifecycle, context injection, and cookie handling."""

    def __init__(self, sessions_dir: Path | str | None = None):
        self.sessions_dir = Path(sessions_dir) if sessions_dir else settings.sessions_dir
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.user_agent = DEFAULT_USER_AGENTS[0]

    def get_session_path(self, platform_name: str) -> Path:
        """Returns session storage path for a platform."""
        return self.sessions_dir / f"{platform_name}_state.json"

    def save_cookies(self, platform_name: str, cookies: list[dict[str, Any]]) -> Path:
        """Save browser session cookies to JSON file."""
        target = self.get_session_path(platform_name)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
        return target

    def load_cookies(self, platform_name: str) -> list[dict[str, Any]] | None:
        """Load saved browser cookies if available."""
        target = self.get_session_path(platform_name)
        if not target.exists():
            return None
        try:
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def get_browser_launch_args(self) -> list[str]:
        """Browser launch arguments to avoid basic bot detection."""
        return [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--window-size=1920,1080",
        ]
