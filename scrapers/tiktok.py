"""
Full TikTok Scraper Engine with Playwright and Network Interception.
Intercepts live API items (item_list / post list) while scrolling through user feeds.
"""
from typing import AsyncGenerator
from playwright.async_api import async_playwright, Response

from config.settings import settings
from core.browser import BrowserManager
from core.models import Platform, SocialPost, UserProfile
from scrapers.base import BaseScraper
from scrapers.tiktok_constants import TIKTOK_BASE_URL
from scrapers.tiktok_profile import parse_tiktok_profile_from_api
from scrapers.tiktok_post import parse_tiktok_video_item

class TikTokScraper(BaseScraper):
    """TikTok scraper leveraging network response interception & stealth browser."""

    def __init__(self, browser_manager: BrowserManager | None = None):
        super().__init__(Platform.TIKTOK)
        self.browser_manager = browser_manager or BrowserManager()

    async def get_profile(self, username: str) -> UserProfile:
        """Fetch profile stats and details for a TikTok creator."""
        cleaned_username = username.lstrip("@")
        profile_url = f"{TIKTOK_BASE_URL}/@{cleaned_username}"
        captured_user: dict = {}
        captured_stats: dict = {}

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.headless,
                args=self.browser_manager.get_browser_launch_args(),
            )
            context = await browser.new_context(
                user_agent=self.browser_manager.user_agent,
                viewport={"width": 1280, "height": 800},
            )

            saved_cookies = self.browser_manager.load_cookies("tiktok")
            if saved_cookies:
                await context.add_cookies(saved_cookies)

            page = await context.new_page()

            async def on_response(response: Response):
                if "/api/user/detail" in response.url or "/user/detail" in response.url:
                    try:
                        data = await response.json()
                        user_info = data.get("userInfo", {})
                        if user_info:
                            captured_user.update(user_info.get("user", {}))
                            captured_stats.update(user_info.get("stats", {}))
                    except Exception:
                        pass

            page.on("response", on_response)
            await page.goto(profile_url, timeout=settings.request_timeout * 1000)
            await self.human_delay(1.5)

            await browser.close()

        if captured_user:
            return parse_tiktok_profile_from_api(captured_user, captured_stats)

        return UserProfile(
            platform=Platform.TIKTOK,
            username=cleaned_username,
            profile_url=profile_url,
        )

    async def get_user_posts(self, username: str, limit: int = 20) -> AsyncGenerator[SocialPost, None]:
        """Stream video posts by scrolling user profile feed."""
        cleaned_username = username.lstrip("@")
        profile_url = f"{TIKTOK_BASE_URL}/@{cleaned_username}"
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

            saved_cookies = self.browser_manager.load_cookies("tiktok")
            if saved_cookies:
                await context.add_cookies(saved_cookies)

            page = await context.new_page()

            async def on_response(response: Response):
                if "/api/post/item_list" in response.url or "/item/list" in response.url:
                    try:
                        payload = await response.json()
                        item_list = payload.get("itemList", []) or payload.get("item_list", [])
                        for item in item_list:
                            vid_id = str(item.get("id") or item.get("aweme_id"))
                            if vid_id and vid_id not in seen_ids:
                                seen_ids.add(vid_id)
                                post = parse_tiktok_video_item(item, default_author=cleaned_username)
                                collected_posts.append(post)
                    except Exception:
                        pass

            page.on("response", on_response)
            await page.goto(profile_url, timeout=settings.request_timeout * 1000)

            for _ in range(max(1, limit // 10)):
                if len(collected_posts) >= limit:
                    break
                await page.evaluate("window.scrollBy(0, 1000)")
                await self.human_delay(1.0)

            await browser.close()

        for post in collected_posts[:limit]:
            yield post

    async def search_posts(self, query: str, limit: int = 20) -> AsyncGenerator[SocialPost, None]:
        """Search videos by tag or keyword."""
        return
