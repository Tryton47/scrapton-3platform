"""
Multi-Link Comment Scraper Engine.
Extracts comments from user-supplied URLs (TikTok, Instagram, and X)
using a robust combination of Network API Interception + DOM Selectors Fallback.
"""
import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator
from playwright.async_api import async_playwright, Response

from config.settings import settings
from core.browser import BrowserManager
from core.models import Platform, SocialComment
from utils.parser import clean_text, parse_abbreviated_number

def detect_platform_from_url(url: str) -> Platform | None:
    """Identify social media platform from link string."""
    url_lower = url.lower()
    if "tiktok.com" in url_lower:
        return Platform.TIKTOK
    elif "instagram.com" in url_lower:
        return Platform.INSTAGRAM
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return Platform.TWITTER
    return None

class CommentScraper:
    """Scrapes comments from user-supplied URLs across TikTok, Instagram, and X."""

    def __init__(self, browser_manager: BrowserManager | None = None):
        self.browser_manager = browser_manager or BrowserManager()

    async def scrape_comments_from_url(self, url: str, max_comments: int = 30) -> list[SocialComment]:
        """Scrape comments from a single URL."""
        platform = detect_platform_from_url(url)
        if not platform:
            return []

        if platform == Platform.TIKTOK:
            return await self._scrape_tiktok_comments(url, max_comments)
        elif platform == Platform.INSTAGRAM:
            return await self._scrape_instagram_comments(url, max_comments)
        elif platform == Platform.TWITTER:
            return await self._scrape_twitter_replies(url, max_comments)
        return []

    async def _scrape_tiktok_comments(self, url: str, max_comments: int) -> list[SocialComment]:
        comments: list[SocialComment] = []
        seen_ids: set[str] = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=settings.headless,
                args=self.browser_manager.get_browser_launch_args(),
            )
            context = await browser.new_context(
                user_agent=self.browser_manager.user_agent,
                viewport={"width": 1280, "height": 900},
            )
            cookies = self.browser_manager.load_cookies("tiktok")
            if cookies:
                await context.add_cookies(cookies)

            page = await context.new_page()

            async def on_response(response: Response):
                if "/comment/list" in response.url or "/api/comment" in response.url:
                    try:
                        payload = await response.json()
                        comment_list = payload.get("comments", []) or []
                        for c in comment_list:
                            cid = str(c.get("cid") or c.get("id"))
                            if cid and cid not in seen_ids:
                                seen_ids.add(cid)
                                user = c.get("user", {})
                                username = user.get("unique_id") or user.get("uniqueId") or "unknown"
                                text = c.get("text") or ""
                                likes = c.get("digg_count") or 0
                                comments.append(SocialComment(
                                    id=cid,
                                    platform=Platform.TIKTOK,
                                    post_url=url,
                                    author_username=username,
                                    author_display_name=user.get("nickname"),
                                    content=clean_text(text),
                                    likes_count=likes,
                                    reply_count=c.get("reply_comment_total", 0),
                                ))
                    except Exception:
                        pass

            page.on("response", on_response)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=settings.request_timeout * 1000)
                await asyncio.sleep(3.0)

                # Try clicking comment button if present to open drawer
                try:
                    await page.click("button[data-e2e='comment-icon'], span[data-e2e='comment-icon']", timeout=3000)
                except Exception:
                    pass

                # Scroll inside comment container or page
                for _ in range(max(3, max_comments // 5)):
                    if len(comments) >= max_comments:
                        break
                    try:
                        await page.mouse.wheel(0, 800)
                    except Exception:
                        pass
                    await asyncio.sleep(1.5)

                # Fallback: DOM Extraction if network API was not intercepted
                if not comments:
                    dom_items = await page.query_selector_all("div[data-e2e='comment-item'], div[class*='CommentItem']")
                    for item in dom_items:
                        if len(comments) >= max_comments:
                            break
                        try:
                            user_el = await item.query_selector("a[data-e2e='comment-username'], span[data-e2e='comment-username']")
                            content_el = await item.query_selector("p[data-e2e='comment-level-1'], div[data-e2e='comment-text']")
                            like_el = await item.query_selector("span[data-e2e='comment-like-count']")

                            username = clean_text(await user_el.inner_text()) if user_el else "unknown"
                            content_text = clean_text(await content_el.inner_text()) if content_el else ""
                            likes_val = parse_abbreviated_number(await like_el.inner_text()) if like_el else 0

                            if content_text:
                                cid = f"dom_{hash(username + content_text)}"
                                if cid not in seen_ids:
                                    seen_ids.add(cid)
                                    comments.append(SocialComment(
                                        id=cid,
                                        platform=Platform.TIKTOK,
                                        post_url=url,
                                        author_username=username,
                                        content=content_text,
                                        likes_count=likes_val,
                                    ))
                        except Exception:
                            continue

            except Exception:
                pass
            finally:
                await browser.close()

        return comments[:max_comments]

    async def _scrape_instagram_comments(self, url: str, max_comments: int) -> list[SocialComment]:
        comments: list[SocialComment] = []
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
            cookies = self.browser_manager.load_cookies("instagram")
            if cookies:
                await context.add_cookies(cookies)

            page = await context.new_page()

            async def on_response(response: Response):
                if "graphql/query" in response.url or "/api/v1/comments" in response.url:
                    try:
                        payload = await response.json()
                        edges = payload.get("data", {}).get("xdt_shortcode_media", {}).get("edge_media_to_parent_comment", {}).get("edges", [])
                        for edge in edges:
                            node = edge.get("node", {})
                            cid = str(node.get("id"))
                            if cid and cid not in seen_ids:
                                seen_ids.add(cid)
                                author = node.get("owner", {}).get("username", "unknown")
                                text = node.get("text", "")
                                likes = node.get("edge_liked_by", {}).get("count", 0)
                                comments.append(SocialComment(
                                    id=cid,
                                    platform=Platform.INSTAGRAM,
                                    post_url=url,
                                    author_username=author,
                                    content=clean_text(text),
                                    likes_count=likes,
                                ))
                    except Exception:
                        pass

            page.on("response", on_response)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=settings.request_timeout * 1000)
                await asyncio.sleep(2.5)

                for _ in range(max(2, max_comments // 10)):
                    if len(comments) >= max_comments:
                        break
                    try:
                        await page.mouse.wheel(0, 600)
                    except Exception:
                        pass
                    await asyncio.sleep(1.5)

                # Fallback DOM for IG
                if not comments:
                    comment_els = await page.query_selector_all("ul ul li[role='menuitem'], div[role='button'] + div span")
                    for el in comment_els:
                        txt = clean_text(await el.inner_text())
                        if txt and len(txt) > 3:
                            cid = f"ig_dom_{hash(txt)}"
                            if cid not in seen_ids:
                                seen_ids.add(cid)
                                comments.append(SocialComment(
                                    id=cid,
                                    platform=Platform.INSTAGRAM,
                                    post_url=url,
                                    author_username="user",
                                    content=txt,
                                ))
            except Exception:
                pass
            finally:
                await browser.close()

        return comments[:max_comments]

    async def _scrape_twitter_replies(self, url: str, max_comments: int) -> list[SocialComment]:
        comments: list[SocialComment] = []
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
            cookies = self.browser_manager.load_cookies("twitter")
            if cookies:
                await context.add_cookies(cookies)

            page = await context.new_page()

            async def on_response(response: Response):
                if "TweetDetail" in response.url or "/graphql/" in response.url:
                    try:
                        data = await response.json()
                        instructions = data.get("data", {}).get("threaded_conversation_with_injections_v2", {}).get("instructions", [])
                        for inst in instructions:
                            entries = inst.get("entries", [])
                            for entry in entries:
                                content = entry.get("content", {})
                                item_content = content.get("itemContent", {})
                                tweet_result = item_content.get("tweet_results", {}).get("result", {})
                                raw_tweet = tweet_result.get("tweet", tweet_result)
                                legacy = raw_tweet.get("legacy", {})
                                if legacy:
                                    cid = str(raw_tweet.get("rest_id") or legacy.get("id_str"))
                                    if cid and cid not in seen_ids:
                                        seen_ids.add(cid)
                                        user_results = raw_tweet.get("core", {}).get("user_results", {}).get("result", {})
                                        author = user_results.get("legacy", {}).get("screen_name", "unknown")
                                        text = legacy.get("full_text", "")
                                        comments.append(SocialComment(
                                            id=cid,
                                            platform=Platform.TWITTER,
                                            post_url=url,
                                            author_username=author,
                                            content=clean_text(text),
                                            likes_count=legacy.get("favorite_count", 0),
                                        ))
                    except Exception:
                        pass

            page.on("response", on_response)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=settings.request_timeout * 1000)
                await asyncio.sleep(2.5)
                for _ in range(max(2, max_comments // 10)):
                    if len(comments) >= max_comments:
                        break
                    try:
                        await page.mouse.wheel(0, 800)
                    except Exception:
                        pass
                    await asyncio.sleep(1.5)
            except Exception:
                pass
            finally:
                await browser.close()

        return comments[:max_comments]
