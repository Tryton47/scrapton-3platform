"""
Session authenticator for Instagram.
Allows interactive browser login to store session state and cookies for bot bypass.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from rich.console import Console

from core.browser import BrowserManager
from scrapers.instagram_constants import INSTAGRAM_LOGIN_URL

console = Console()

class InstagramAuth:
    """Manages manual / interactive login and cookie saving for Instagram."""

    def __init__(self, browser_manager: BrowserManager | None = None):
        self.browser_manager = browser_manager or BrowserManager()

    async def login_interactive(self, timeout_seconds: int = 120) -> bool:
        """
        Launches a visible browser window allowing the user to solve login / 2FA.
        Saves session cookies automatically upon successful login.
        """
        console.print("[bold yellow]Opening visible browser for Instagram login...[/bold yellow]")
        console.print("[dim]Please log in to your Instagram account in the opened window.[/dim]")

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
            await page.goto(INSTAGRAM_LOGIN_URL)

            # Wait until user navigates away from login page or sessionid cookie appears
            console.print(f"[cyan]Waiting up to {timeout_seconds}s for login completion...[/cyan]")
            logged_in = False
            for _ in range(timeout_seconds // 2):
                await asyncio.sleep(2)
                cookies = await context.cookies()
                cookie_names = [c["name"] for c in cookies]
                if "sessionid" in cookie_names:
                    logged_in = True
                    break

            if logged_in:
                cookies = await context.cookies()
                session_path = self.browser_manager.save_cookies("instagram", cookies)
                console.print(f"[bold green]Login successful! Session cookies saved to: {session_path}[/bold green]")
            else:
                console.print("[bold red]Login timed out or sessionid not found.[/bold red]")

            await browser.close()
            return logged_in

    def has_saved_session(self) -> bool:
        """Check if saved cookies exist."""
        return self.browser_manager.load_cookies("instagram") is not None
