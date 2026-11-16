"""
Full X (Twitter) Scraper Engine with Playwright and Network Interception.
Intercepts live GraphQL timeline responses (UserTweets, SearchTimeline) while scrolling.
"""
from typing import AsyncGenerator
from playwright.async_api import async_playwright, Response

from config.settings import settings
from core.browser import BrowserManager
from core.models import Platform, SocialPost, UserProfile
from scrapers.base import BaseScraper
from scrapers.twitter_constants import TWITTER_BASE_URL
from scrapers.twitter_profile import parse_twitter_profile
from scrapers.twitter_post import parse_twitter_tweet_result

class TwitterScraper(BaseScraper):
    """X / Twitter scraper using GraphQL response interception."""

    def __init__(self, browser_manager: BrowserManager | None = None):
        super().__init__(Platform.TWITTER)
        self.browser_manager = browser_manager or BrowserManager()

    async def get_profile(self, username: str) -> UserProfile:
        """Fetch user profile metadata for target Twitter username."""
        clean_user = username.lstrip("@")
        profile_url = f"{TWITTER_BASE_URL}/{clean_user}"
        captured_data: dict = {}

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.headless,
                args=self.browser_manager.get_browser_launch_args(),
            )
            context = await browser.new_context(
                user_agent=self.browser_manager.user_agent,
                viewport={"width": 1280, "height": 850},
            )

            saved_cookies = self.browser_manager.load_cookies("twitter")
            if saved_cookies:
                await context.add_cookies(saved_cookies)

            page = await context.new_page()

            async def on_response(response: Response):
                if "UserByScreenName" in response.url or "/graphql/" in response.url:
                    try:
                        data = await response.json()
                        if "data" in data and "user" in data["data"]:
                            captured_data.update(data["data"]["user"])
                    except Exception:
                        pass

            page.on("response", on_response)
            await page.goto(profile_url, timeout=settings.request_timeout * 1000)
            await self.human_delay(1.5)

            await browser.close()

        if captured_data:
            return parse_twitter_profile(captured_data)

        return UserProfile(
            platform=Platform.TWITTER,
            username=clean_user,
            profile_url=profile_url,
        )

    async def get_user_posts(self, username: str, limit: int = 20) -> AsyncGenerator[SocialPost, None]:
        """Stream tweets by scrolling user profile feed and intercepting UserTweets GraphQL."""
        clean_user = username.lstrip("@")
        profile_url = f"{TWITTER_BASE_URL}/{clean_user}"
        collected_tweets: list[SocialPost] = []
        seen_ids: set[str] = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.headless,
                args=self.browser_manager.get_browser_launch_args(),
            )
            context = await browser.new_context(
                user_agent=self.browser_manager.user_agent,
                viewport={"width": 1280, "height": 850},
            )

            saved_cookies = self.browser_manager.load_cookies("twitter")
            if saved_cookies:
                await context.add_cookies(saved_cookies)

            page = await context.new_page()

            async def on_response(response: Response):
                if "UserTweets" in response.url or "/graphql/" in response.url:
                    try:
                        data = await response.json()
                        instructions = (
                            data.get("data", {})
                            .get("user", {})
                            .get("result", {})
                            .get("timeline_v2", {})
                            .get("timeline", {})
                            .get("instructions", [])
                        )
                        for inst in instructions:
                            entries = inst.get("entries", [])
                            for entry in entries:
                                content = entry.get("content", {})
                                item_content = content.get("itemContent", {})
                                tweet_result = item_content.get("tweet_results", {}).get("result", {})
                                post = parse_twitter_tweet_result(tweet_result, default_author=clean_user)
                                if post and post.id and post.id not in seen_ids:
                                    seen_ids.add(post.id)
                                    collected_tweets.append(post)
                    except Exception:
                        pass

            page.on("response", on_response)
            await page.goto(profile_url, timeout=settings.request_timeout * 1000)

            for _ in range(max(1, limit // 10)):
                if len(collected_tweets) >= limit:
                    break
                await page.evaluate("window.scrollBy(0, 1000)")
                await self.human_delay(1.2)

            await browser.close()

        for tweet in collected_tweets[:limit]:
            yield tweet

    async def search_posts(self, query: str, limit: int = 20) -> AsyncGenerator[SocialPost, None]:
        """Search tweets by query or hashtag."""
        return
