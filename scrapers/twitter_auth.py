"""
Interactive session authenticator for X (Twitter).
Launches browser to log in and saves cookies (auth_token & ct0) for authenticated requests.
"""
import asyncio
from playwright.async_api import async_playwright
from rich.console import Console

from core.browser import BrowserManager
from scrapers.twitter_constants import TWITTER_LOGIN_URL

console = Console()

class TwitterAuth:
    """Manages X / Twitter interactive authentication and session saving."""

    def __init__(self, browser_manager: BrowserManager | None = None):
        self.browser_manager = browser_manager or BrowserManager()

    async def login_interactive(self, timeout_seconds: int = 150) -> bool:
        """
        Launches visible browser for X/Twitter login flow (password, 2FA, confirm).
        Captures and persists auth_token and ct0 session cookies.
        """
        console.print("[bold yellow]Opening visible browser for X (Twitter) login...[/bold yellow]")
        console.print("[dim]Please complete login in the opened window.[/dim]")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=self.browser_manager.get_browser_launch_args(),
            )
            context = await browser.new_context(
                user_agent=self.browser_manager.user_agent,
                viewport={"width": 1280, "height": 850},
            )
            page = await context.new_page()
            await page.goto(TWITTER_LOGIN_URL)

            console.print(f"[cyan]Waiting up to {timeout_seconds}s for login completion...[/cyan]")
            logged_in = False
            for _ in range(timeout_seconds // 2):
                await asyncio.sleep(2)
                cookies = await context.cookies()
                cookie_names = [c["name"] for c in cookies]
                if "auth_token" in cookie_names and "ct0" in cookie_names:
                    logged_in = True
                    break

            if logged_in:
                cookies = await context.cookies()
                session_path = self.browser_manager.save_cookies("twitter", cookies)
                console.print(f"[bold green]X (Twitter) login successful! Cookies saved to: {session_path}[/bold green]")
            else:
                console.print("[bold red]X login timed out or auth_token cookie not found.[/bold red]")

            await browser.close()
            return logged_in

    def has_saved_session(self) -> bool:
        """Check if saved cookies exist."""
        return self.browser_manager.load_cookies("twitter") is not None
