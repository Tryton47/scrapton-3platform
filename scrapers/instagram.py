"""
Full Instagram Scraper Engine with Playwright and Network Interception.
Intercepts live GraphQL / API responses while scrolling to extract high-fidelity post data.
"""
import asyncio
from typing import AsyncGenerator
from playwright.async_api import async_playwright, Response

from config.settings import settings
from core.browser import BrowserManager
from core.models import Platform, SocialPost, UserProfile
from scrapers.base import BaseScraper
from scrapers.instagram_constants import INSTAGRAM_BASE_URL, INSTAGRAM_HEADERS
from scrapers.instagram_profile import parse_profile_from_api_json
from scrapers.instagram_post import parse_instagram_post_node

class InstagramScraper(BaseScraper):
    """Instagram scraper leveraging network response interception & stealth browser."""

    def __init__(self, browser_manager: BrowserManager | None = None):
        super().__init__(Platform.INSTAGRAM)
        self.browser_manager = browser_manager or BrowserManager()

    async def get_profile(self, username: str) -> UserProfile:
        """Fetch profile information for a target Instagram user."""
        profile_url = f"{INSTAGRAM_BASE_URL}/{username}/"
        captured_data: dict = {}

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.headless,
                args=self.browser_manager.get_browser_launch_args(),
            )
            context = await browser.new_context(
                user_agent=self.browser_manager.user_agent,
                viewport={"width": 1280, "height": 800},
            )

            # Load cookies if available
            saved_cookies = self.browser_manager.load_cookies("instagram")
            if saved_cookies:
                await context.add_cookies(saved_cookies)

            page = await context.new_page()

            # Intercept response containing profile info
            async def on_response(response: Response):
                if "/api/v1/users/web_profile_info/" in response.url or "graphql/query" in response.url:
                    try:
                        data = await response.json()
                        if "data" in data and "user" in data["data"]:
                            captured_data.update(data)
                    except Exception:
                        pass

            page.on("response", on_response)
            await page.goto(profile_url, timeout=settings.request_timeout * 1000)
            await self.human_delay(1.5)

            await browser.close()

        if captured_data:
            return parse_profile_from_api_json(captured_data)

        # Fallback profile if API was not caught directly
        return UserProfile(
            platform=Platform.INSTAGRAM,
            username=username,
            profile_url=profile_url,
        )

    async def get_user_posts(self, username: str, limit: int = 20) -> AsyncGenerator[SocialPost, None]:
        """Stream posts by scrolling and intercepting GraphQL timeline responses."""
        profile_url = f"{INSTAGRAM_BASE_URL}/{username}/"
        collected_posts: list[SocialPost] = []
        seen_ids: set[str] = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.headless,
                args=self.browser_manager.get_browser_launch_args(),
            )
            context = await browser.new_context(
                user_agent=self.browser_manager.user_agent,
                viewport={"width": 1280, "height": 800},
            )

            saved_cookies = self.browser_manager.load_cookies("instagram")
            if saved_cookies:
                await context.add_cookies(saved_cookies)

            page = await context.new_page()

            async def on_response(response: Response):
                if "graphql/query" in response.url or "/api/v1/users/web_profile_info/" in response.url:
                    try:
                        payload = await response.json()
                        user = payload.get("data", {}).get("user", {})
                        timeline = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
                        for edge in timeline:
                            node = edge.get("node", {})
                            post_id = str(node.get("id"))
                            if post_id and post_id not in seen_ids:
                                seen_ids.add(post_id)
                                post = parse_instagram_post_node(node, default_author=username)
                                collected_posts.append(post)
                    except Exception:
                        pass

            page.on("response", on_response)
            await page.goto(profile_url, timeout=settings.request_timeout * 1000)

            # Scroll loop to trigger feed loading
            for _ in range(max(1, limit // 10)):
                if len(collected_posts) >= limit:
                    break
                try:
                    await page.mouse.wheel(0, 1000)
                except Exception:
                    pass
                await self.human_delay(1.0)

            await browser.close()

        for post in collected_posts[:limit]:
            yield post

    async def search_posts(self, query: str, limit: int = 20) -> AsyncGenerator[SocialPost, None]:
        """Search hashtag posts."""
        hashtag = query.lstrip("#")
        tag_url = f"{INSTAGRAM_BASE_URL}/explore/tags/{hashtag}/"
        yielded = 0

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=settings.headless)
            page = await browser.new_page()
            await page.goto(tag_url, timeout=settings.request_timeout * 1000)
            await self.human_delay(1.0)
            await browser.close()

        # Generator stub for search
        return
