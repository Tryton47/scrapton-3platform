"""
Interactive session authenticator for TikTok.
Launches browser for login and saves session cookies to bypass bot wall.
"""
import asyncio
from playwright.async_api import async_playwright
from rich.console import Console

from core.browser import BrowserManager
from scrapers.tiktok_constants import TIKTOK_LOGIN_URL

console = Console()

class TikTokAuth:
    """Manages TikTok interactive login and session cookie persistence."""

    def __init__(self, browser_manager: BrowserManager | None = None):
        self.browser_manager = browser_manager or BrowserManager()

    async def login_interactive(self, timeout_seconds: int = 120) -> bool:
        """
        Launches visible browser for TikTok login (handles captcha/QR/OAuth).
        Saves session cookies upon detecting sessionid or sid_guard.
        """
        console.print("[bold yellow]Opening visible browser for TikTok login...[/bold yellow]")
        console.print("[dim]Please complete login or solve captcha in the opened window.[/dim]")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=self.browser_manager.get_browser_launch_args(),
            )
            context = await browser.new_context(
                user_agent=self.browser_manager.user_agent,
                viewport={"width": 1280, "height": 800},
            )
            page = await context.new_page()
            await page.goto(TIKTOK_LOGIN_URL)

            console.print(f"[cyan]Waiting up to {timeout_seconds}s for login completion...[/cyan]")
            logged_in = False
            for _ in range(timeout_seconds // 2):
                await asyncio.sleep(2)
                cookies = await context.cookies()
                cookie_names = [c["name"] for c in cookies]
                if "sessionid" in cookie_names or "sid_guard" in cookie_names or "sessionid_ss" in cookie_names:
                    logged_in = True
                    break

            if logged_in:
                cookies = await context.cookies()
                session_path = self.browser_manager.save_cookies("tiktok", cookies)
                console.print(f"[bold green]TikTok login successful! Cookies saved to: {session_path}[/bold green]")
            else:
                console.print("[bold red]TikTok login timed out or session token not found.[/bold red]")

            await browser.close()
            return logged_in

    def has_saved_session(self) -> bool:
        """Check if TikTok cookies exist."""
        return self.browser_manager.load_cookies("tiktok") is not None
